"""Boot the local server, run commands against it over RCON, stop it, and hand back the console.

The obvious harness - start the process and read its stdout until you see what you want - hangs the
moment the server goes idle, because readline() blocks forever on a server that has nothing to say.
This one stops reading as soon as "Done (" appears, does its work through RCON instead, and takes the
rest of the console from logs/latest.log after the process has exited.

    localtest.py "cmd one" "cmd two" ...        run these, then stop
    localtest.py --grep PATTERN "cmd" ...       also print boot lines matching PATTERN
    localtest.py --boot-only                    just boot and stop, for a clean-start check

Everything here is the LOCAL server at G:/GSCraft/server on port 9150. It never touches the host.
"""
import re
import select
import socket
import struct
import subprocess
import sys
import threading
import time
from pathlib import Path

SERVER = Path(r"G:/GSCraft/server")
RCON_HOST, RCON_PORT = "127.0.0.1", 25575
RCON_PASS = "gscraft-local-test"
BOOT_TIMEOUT = 600
# what run.bat passes; going through cmd /c never produced a java process from here
JVM_ARGS = "user_jvm_args.txt"
FORGE_ARGS = "libraries/net/minecraftforge/forge/1.20.1-47.4.23/win_args.txt"


class Rcon:
    """Source RCON. Small enough that a dependency would cost more than it saves."""

    def __init__(self, host, port, password):
        self.s = socket.create_connection((host, port), timeout=30)
        self.i = 0
        if self._send(3, password) is None:
            raise SystemExit("rcon: authentication failed")

    def _pack(self, kind, body):
        self.i += 1
        payload = struct.pack("<ii", self.i, kind) + body.encode("utf-8") + b"\x00\x00"
        return struct.pack("<i", len(payload)) + payload, self.i

    def _send(self, kind, body):
        pkt, want = self._pack(kind, body)
        self.s.sendall(pkt)
        size = struct.unpack("<i", self._read(4))[0]
        rid, _ = struct.unpack("<ii", self._read(8))
        data = self._read(size - 8)[:-2].decode("utf-8", "replace")
        return None if rid == -1 else (data if rid == want else data)

    def _read(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self.s.recv(n - len(buf))
            if not chunk:
                raise SystemExit("rcon: connection closed")
            buf += chunk
        return buf

    def cmd(self, c, timeout=20):
        # a command that writes only to the console answers with nothing; that is an answer, not a fault
        self.s.settimeout(timeout)
        try:
            return self._send(2, c)
        except (socket.timeout, TimeoutError):
            return "(no reply - the command answers on the console, not to rcon)"

    def close(self):
        try:
            self.s.close()
        except Exception:
            pass


def boot():
    """Start the server and return the process once it says Done, plus the boot lines seen."""
    args = ["java", f"@{JVM_ARGS}", f"@{FORGE_ARGS}", "nogui"]
    p = subprocess.Popen(args, cwd=str(SERVER),
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace",
                         bufsize=1)
    lines, ready = [], threading.Event()

    def pump():
        # read only until the server is up; after that the log file is the record and this thread
        # would otherwise block forever on an idle server
        for line in p.stdout:
            lines.append(line.rstrip("\n"))
            if "Done (" in line:
                ready.set()
                break

    t = threading.Thread(target=pump, daemon=True)
    t.start()
    if not ready.wait(BOOT_TIMEOUT):
        p.kill()
        print("\n".join(lines[-40:]))
        raise SystemExit(f"server did not reach Done within {BOOT_TIMEOUT}s")
    return p, lines


def main(argv):
    grep = None
    if "--grep" in argv:
        i = argv.index("--grep")
        grep = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    cmds = [a for a in argv[1:] if not a.startswith("--")]

    t0 = time.time()
    print(f"booting the local server ({SERVER})...")
    p, lines = boot()
    print(f"up in {time.time() - t0:.0f}s")

    out = {}
    time.sleep(3)                          # let the first tick settle before asking anything
    r = Rcon(RCON_HOST, RCON_PORT, RCON_PASS)
    try:
        for c in cmds:
            out[c] = r.cmd(c)
            print(f"\n> {c}\n{out[c]}")
            time.sleep(0.4)
    finally:
        # whatever happened above, the server comes down - a harness that leaves one running is worse
        # than one that fails
        try:
            r.cmd("stop", timeout=30)
        except Exception as e:
            print(f"could not send stop over rcon ({e}); killing the process")
            p.kill()
        r.close()

    try:
        p.wait(timeout=180)
    except subprocess.TimeoutExpired:
        p.kill()

    if grep:
        log = (SERVER / "logs" / "latest.log").read_text(encoding="utf-8", errors="replace")
        hits = [l for l in log.splitlines() if re.search(grep, l, re.I)]
        print(f"\n--- boot lines matching /{grep}/ : {len(hits)} ---")
        for l in hits[:60]:
            print("  ", l)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
