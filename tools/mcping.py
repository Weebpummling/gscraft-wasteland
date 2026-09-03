"""Server-list ping (vanilla status protocol): reachability, version, MOTD, player count, and the
Forge mod list the server advertises in its status response. No login, no account needed.

usage: mcping.py <host> <port>
"""
import json, socket, struct, sys, time


def varint(n):
    out = b""
    while True:
        b = n & 0x7F; n >>= 7
        if n: out += bytes([b | 0x80])
        else: return out + bytes([b])


def read_varint(sock):
    n = 0; shift = 0
    while True:
        b = sock.recv(1)
        if not b: raise ConnectionError("closed")
        n |= (b[0] & 0x7F) << shift; shift += 7
        if not b[0] & 0x80: return n


def packet(pid, payload):
    body = varint(pid) + payload
    return varint(len(body)) + body


def main(argv):
    host, port = argv[1], int(argv[2])
    t = time.time()
    s = socket.create_connection((host, port), timeout=8)
    hs = varint(763) + varint(len(host.encode())) + host.encode() + struct.pack(">H", port) + varint(1)
    s.sendall(packet(0, hs) + packet(0, b""))
    length = read_varint(s); pid = read_varint(s); jl = read_varint(s)
    data = b""
    while len(data) < jl:
        chunk = s.recv(jl - len(data))
        if not chunk: break
        data += chunk
    rtt = int((time.time() - t) * 1000); s.close()
    st = json.loads(data.decode("utf-8", "replace"))
    desc = st.get("description"); desc = desc.get("text", "") if isinstance(desc, dict) else str(desc)
    print(f"reachable {host}:{port}  rtt {rtt} ms")
    print("version:", st.get("version", {}).get("name"), "protocol", st.get("version", {}).get("protocol"))
    print("motd:", desc)
    print("players:", st.get("players", {}).get("online"), "/", st.get("players", {}).get("max"))
    fd = st.get("forgeData") or {}
    mods = fd.get("mods") or []
    if fd:
        print("forge status: fmlNetworkVersion", fd.get("fmlNetworkVersion"), "mods advertised:", len(mods) if isinstance(mods, list) else "(compressed d field)")
        if isinstance(mods, list) and mods: print("  sample:", ", ".join(m.get("modId", "?") for m in mods[:12]))
    else:
        print("no forgeData in status (a vanilla or non-Forge server)")


if __name__ == "__main__":
    main(sys.argv)
