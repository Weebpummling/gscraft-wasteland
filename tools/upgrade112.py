"""Let the vanilla 1.20.1 server flatten a 1.12.2 save (the vanilla layer of the foreign-build pipeline).

usage: upgrade112.py <1.12 save dir> <work dir> [--vanilla-jar <path>] [--java <path>]

Copies the save into <work dir>/world (level.dat, region/, data/ only - no modded dimensions or
mod data), points a vanilla server at it and runs `--forceUpgrade --eraseCache`, waits for the
server to report Done, sends `stop`, and prints what the upgrade log said. The upgraded world is
<work dir>/world; read it with the 1.20 tools (topdown.py, anvil.py).

The vanilla jar is the one the Forge installer fetched:
  G:/GSCraft/server/libraries/net/minecraft/server/1.20.1/server-1.20.1.jar
eula.txt is copied from G:/GSCraft/server (the owner's acceptance) - it is not written here.
"""
import sys, shutil, subprocess, time, re, gzip, struct
from pathlib import Path

VANILLA = Path(r"G:/GSCraft/server/libraries/net/minecraft/server/1.20.1/server-1.20.1.jar")
EULA_SRC = Path(r"G:/GSCraft/server/eula.txt")
JAVA = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.8-hotspot\bin\java.exe"


def prepare(save: Path, work: Path):
    world = work / "world"
    if world.exists():
        shutil.rmtree(world)
    world.mkdir(parents=True)
    shutil.copy2(save / "level.dat", world / "level.dat")
    shutil.copytree(save / "region", world / "region")
    if (save / "data").exists():
        shutil.copytree(save / "data", world / "data")
    if not EULA_SRC.exists() or "eula=true" not in EULA_SRC.read_text():
        sys.exit("G:/GSCraft/server/eula.txt does not say eula=true; nothing run")
    shutil.copy2(EULA_SRC, work / "eula.txt")
    (work / "server.properties").write_text(
        "level-name=world\nonline-mode=false\nserver-port=25599\nmax-players=0\nspawn-protection=0\n"
        "enable-command-block=false\nlevel-type=minecraft\\:normal\nmotd=upgrade\ndifficulty=peaceful\n"
        "spawn-monsters=false\nspawn-animals=false\nspawn-npcs=false\nview-distance=2\nsimulation-distance=2\n",
        encoding="utf-8")
    return world


def run(work: Path, jar: Path, java: str):
    cmd = [java, "-Xms1G", "-Xmx6G", "-jar", str(jar), "--forceUpgrade", "--eraseCache", "--nogui"]
    log = open(work / "upgrade-console.log", "w", encoding="utf-8")
    p = subprocess.Popen(cmd, cwd=work, stdin=subprocess.PIPE, stdout=log, stderr=subprocess.STDOUT, text=True)
    t0 = time.time(); done = False
    while p.poll() is None and time.time() - t0 < 3600:
        time.sleep(5)
        txt = (work / "upgrade-console.log").read_text(encoding="utf-8", errors="replace")
        if "Done (" in txt and not done:
            done = True
            p.stdin.write("stop\n"); p.stdin.flush()
        if "Failed to load eula.txt" in txt or "You need to agree to the EULA" in txt:
            p.kill(); sys.exit("EULA not accepted in the work dir")
    if p.poll() is None:
        p.kill(); sys.exit("upgrade timed out after 60 min")
    txt = (work / "upgrade-console.log").read_text(encoding="utf-8", errors="replace")
    for line in txt.splitlines():
        if re.search(r"Upgrad|upgrad|chunks|Done \(|ERROR|Exception|Converting", line):
            print("  " + line.strip()[:200])
    return p.returncode


def main(a):
    if len(a) < 3:
        sys.exit(__doc__)
    save, work = Path(a[1]), Path(a[2])
    jar = Path(a[a.index("--vanilla-jar") + 1]) if "--vanilla-jar" in a else VANILLA
    java = a[a.index("--java") + 1] if "--java" in a else JAVA
    world = prepare(save, work)
    print(f"prepared {world}; running vanilla --forceUpgrade")
    rc = run(work, jar, java)
    print(f"server exit {rc}; upgraded world at {world}")


if __name__ == "__main__":
    main(sys.argv)
