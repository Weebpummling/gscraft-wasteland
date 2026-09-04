"""Build the GSCraft client installer set: a packwiz pack (auto-updating), a Modrinth .mrpack, a tiny Prism
instance zip that self-installs the pack on first launch, the Windows setup .cmd, and the release assets
for the jars Modrinth does not host.  docs/notes/gscraft-one-click-install.md is the design.

usage: packwiz_build.py [--tag client-installer-YYYY-MM-DD] [--version YYYY.MM.DD]

Inputs (this machine): G:/GSCraft/server/mods (the pinned jar set), G:/GSCraft/server/config (the pack's
config), the Prism instance's client-only configs / defaultconfigs / servers.dat / tacz packs,
build/kubejs, scratch/modrinth_files.json (from the Modrinth hash lookup).
Outputs: build/packwiz/ (commit + push: served from raw.githubusercontent.com) and
G:/GSCraft/release-installer/ (upload to the GitHub release <tag>).

Text files are written with LF line endings and build/packwiz/.gitattributes switches git's conversion
off, so the bytes GitHub serves are the bytes hashed into index.toml.
"""
import hashlib, json, re, shutil, sys, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
G = Path("G:/GSCraft")
SERVER_MODS = G / "server" / "mods"
SERVER_CONFIG = G / "server" / "config"
INST = G / "client" / "instances" / "GSCraft"
MC = INST / ".minecraft"
MODRINTH = json.load(open(G / "scratch" / "modrinth_files.json", encoding="utf-8"))

TAG = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else "client-installer-2026-09-04"
VERSION = sys.argv[sys.argv.index("--version") + 1] if "--version" in sys.argv else "2026.09.04"
GH_REPO = "Weebpummling/gscraft-wasteland"
RAW = f"https://raw.githubusercontent.com/{GH_REPO}/main/build/packwiz/"
REL = f"https://github.com/{GH_REPO}/releases/download/{TAG}/"
PRISM_VER = "11.1.0"
PRISM_ZIP = f"https://github.com/PrismLauncher/PrismLauncher/releases/download/{PRISM_VER}/PrismLauncher-Windows-MSVC-Portable-{PRISM_VER}.zip"
BOOTSTRAP = G / "incoming" / "tools" / "packwiz-installer-bootstrap.jar"

OUT = REPO / "build" / "packwiz"
ASSETS = G / "release-installer"
CLIENT_ONLY = {"xaerominimap", "xaeroworldmap"}           # jar-name prefixes that never run on the server
CONFIG_SKIP = {"QuantifiedAPI", "spark", "chunky", "worldedit", "xaero", "FML.VersionCheck.txt", "voicechat"}
CLIENT_CONFIG_EXTRA = ["appleskin-client.toml", "lootr-client.toml", "recruits-client.toml", "pingwheel.server.json"]
TEXT_EXT = {".toml", ".json", ".json5", ".cfg", ".properties", ".txt", ".js", ".snbt", ".md"}
CRLF = b"\r\n"
LF = b"\n"


def sha(p, algo):
    h = hashlib.new(algo); h.update(Path(p).read_bytes()); return h.hexdigest()


def toml_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def asset_name(name):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_")


def reset(d: Path):
    if d.exists(): shutil.rmtree(d)
    d.mkdir(parents=True)


def copy_norm(src: Path, dst: Path):
    """Copy a file; text files get LF line endings (see the module docstring)."""
    if src.suffix.lower() in TEXT_EXT:
        dst.write_bytes(src.read_bytes().replace(CRLF, LF))
    else:
        shutil.copy2(src, dst)


def copy_tree(src: Path, dst: Path, skip=()):
    out = []
    for p in sorted(src.rglob("*")):
        rel = p.relative_to(src)
        if any(part in skip for part in rel.parts): continue
        if p.is_file():
            (dst / rel).parent.mkdir(parents=True, exist_ok=True); copy_norm(p, dst / rel); out.append(rel.as_posix())
    return out


def main():
    reset(OUT); reset(ASSETS)
    (OUT / "mods").mkdir(); (OUT / "tacz").mkdir()
    (OUT / ".gitattributes").write_bytes(b"* -text\n")
    index_files = []          # (path, hash, metafile)
    mr_files = []             # mrpack file entries
    jars = sorted(p for p in SERVER_MODS.glob("*.jar"))
    hosted = missing = 0
    for jar in jars:
        name = jar.name
        side = "client" if any(name.lower().startswith(c) for c in CLIENT_ONLY) else "both"
        s512, s1 = sha(jar, "sha512"), sha(jar, "sha1")
        if name in MODRINTH:
            m = MODRINTH[name]; url = m["url"]; hosted += 1
            update = f'\n[update]\n[update.modrinth]\nmod-id = {toml_str(m["project_id"])}\nversion = {toml_str(m["version_id"])}\n'
        else:
            an = asset_name(name); shutil.copy2(jar, ASSETS / an); url = REL + an; update = ""; missing += 1
        stem = re.sub(r"[^a-z0-9]+", "-", name[:-4].lower()).strip("-")
        meta = OUT / "mods" / f"{stem}.pw.toml"
        meta.write_bytes((f"name = {toml_str(name[:-4])}\nfilename = {toml_str(name)}\nside = \"{side}\"\n\n[download]\n"
                          f"url = {toml_str(url)}\nhash-format = \"sha512\"\nhash = \"{s512}\"\n{update}").encode("utf-8"))
        index_files.append((f"mods/{stem}.pw.toml", sha(meta, "sha256"), True))
        mr_files.append({"path": f"mods/{name}", "hashes": {"sha1": s1, "sha512": s512},
                         "env": {"client": "required", "server": "unsupported" if side == "client" else "required"},
                         "downloads": [url], "fileSize": jar.stat().st_size})
    # TaCZ gun packs beside the default one (TaCZ re-extracts its own default pack on every client start)
    for z in sorted((MC / "tacz").glob("*.zip")):
        an = asset_name(z.name); shutil.copy2(z, ASSETS / an); url = REL + an
        stem = re.sub(r"[^a-z0-9]+", "-", z.stem.lower()).strip("-")
        meta = OUT / "tacz" / f"{stem}.pw.toml"
        meta.write_bytes((f"name = {toml_str(z.stem)}\nfilename = {toml_str(z.name)}\nside = \"both\"\n\n[download]\n"
                          f"url = {toml_str(url)}\nhash-format = \"sha512\"\nhash = \"{sha(z, 'sha512')}\"\n").encode("utf-8"))
        index_files.append((f"tacz/{stem}.pw.toml", sha(meta, "sha256"), True))
        mr_files.append({"path": f"tacz/{z.name}", "hashes": {"sha1": sha(z, "sha1"), "sha512": sha(z, "sha512")},
                         "env": {"client": "required", "server": "required"}, "downloads": [url], "fileSize": z.stat().st_size})
    # plain files: config (the server's = the pack's), client-only configs, kubejs (repo), defaultconfigs, servers.dat, tacz-pre.toml
    plain = ["config/" + p for p in copy_tree(SERVER_CONFIG, OUT / "config", skip=CONFIG_SKIP)]
    for f in CLIENT_CONFIG_EXTRA:
        src = MC / "config" / f
        if src.exists() and not (OUT / "config" / f).exists():
            copy_norm(src, OUT / "config" / f); plain.append("config/" + f)
    plain += ["kubejs/" + p for p in copy_tree(REPO / "build" / "kubejs", OUT / "kubejs")]
    plain += ["defaultconfigs/" + p for p in copy_tree(MC / "defaultconfigs", OUT / "defaultconfigs")]
    for rel in ("servers.dat", "tacz/tacz-pre.toml"):
        src = MC / rel; (OUT / rel).parent.mkdir(parents=True, exist_ok=True); copy_norm(src, OUT / rel); plain.append(rel)
    for rel in plain:
        index_files.append((rel, sha(OUT / rel, "sha256"), False))
    # index.toml and pack.toml
    lines = ['hash-format = "sha256"', ""]
    for rel, h, meta in sorted(index_files):
        lines += ["[[files]]", f"file = {toml_str(rel)}", f'hash = "{h}"'] + (["metafile = true"] if meta else []) + [""]
    (OUT / "index.toml").write_bytes("\n".join(lines).encode("utf-8"))
    (OUT / "pack.toml").write_bytes((
        f'name = "GSCraft"\nauthor = "GSCraft"\nversion = {toml_str(VERSION)}\npack-format = "packwiz:1.1.0"\n\n'
        f'[index]\nfile = "index.toml"\nhash-format = "sha256"\nhash = "{sha(OUT / "index.toml", "sha256")}"\n\n'
        f'[versions]\nforge = "47.4.10"\nminecraft = "1.20.1"\n').encode("utf-8"))
    # .mrpack: the same files, overrides = the plain files
    mr = {"formatVersion": 1, "game": "minecraft", "versionId": VERSION, "name": "GSCraft",
          "summary": "GSCraft wasteland - Minecraft 1.20.1 Forge 47.4.10", "files": mr_files,
          "dependencies": {"minecraft": "1.20.1", "forge": "47.4.10"}}
    with zipfile.ZipFile(ASSETS / "GSCraft.mrpack", "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("modrinth.index.json", json.dumps(mr, indent=1))
        for rel in plain:
            z.write(OUT / rel, "overrides/" + rel)
    # the Prism instance zip: instance.cfg with the packwiz pre-launch command (Prism's own escaped form), bootstrap jar, servers.dat
    cfg = (INST / "instance.cfg").read_text(encoding="utf-8").rstrip("\n").splitlines()
    cfg = [l for l in cfg if not l.startswith(("OverrideCommands", "PreLaunchCommand", "notes"))]
    pre = '\\"$INST_JAVA\\" -jar packwiz-installer-bootstrap.jar ' + RAW + "pack.toml"
    cfg += ["OverrideCommands=true", "PreLaunchCommand=" + pre,
            f"notes=GSCraft {VERSION} - the pack installs and updates itself on every launch (packwiz)"]
    with zipfile.ZipFile(ASSETS / "GSCraft-Instance.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("instance.cfg", "\n".join(cfg) + "\n")
        z.write(INST / "mmc-pack.json", "mmc-pack.json")
        z.write(BOOTSTRAP, ".minecraft/packwiz-installer-bootstrap.jar")
        z.write(MC / "servers.dat", ".minecraft/servers.dat")
    # the Windows setup file (CRLF, ASCII)
    cmd = "\r\n".join([
        "@echo off", "setlocal", "title GSCraft setup",
        'set "DIR=%LOCALAPPDATA%\\GSCraft\\Prism"',
        f'set "PRISM={PRISM_ZIP}"',
        f'set "PACK={REL}GSCraft-Instance.zip"',
        "echo.",
        "echo  GSCraft setup - this installs Prism Launcher (portable) and the GSCraft instance.",
        "echo  The pack itself (about 450 MB) downloads on the first Play; later launches only fetch changes.",
        "echo.",
        'if not exist "%DIR%\\prismlauncher.exe" (',
        '  mkdir "%DIR%" 2>nul',
        f"  echo  Downloading Prism Launcher {PRISM_VER} ...",
        "  powershell -NoProfile -ExecutionPolicy Bypass -Command \"[Net.ServicePointManager]::SecurityProtocol='Tls12'; "
        "Invoke-WebRequest -Uri '%PRISM%' -OutFile '%TEMP%\\prism.zip'; Expand-Archive -Path '%TEMP%\\prism.zip' -DestinationPath '%DIR%' -Force\" || goto :fail",
        '  if not exist "%DIR%\\portable.txt" type nul > "%DIR%\\portable.txt"',
        ")",
        "echo  Downloading the GSCraft instance ...",
        "powershell -NoProfile -ExecutionPolicy Bypass -Command \"[Net.ServicePointManager]::SecurityProtocol='Tls12'; "
        "Invoke-WebRequest -Uri '%PACK%' -OutFile '%TEMP%\\GSCraft-Instance.zip'\" || goto :fail",
        "echo  Opening Prism Launcher. Sign in with your Microsoft account when it asks, then press Play on GSCraft.",
        'start "" "%DIR%\\prismlauncher.exe" --import "%TEMP%\\GSCraft-Instance.zip"',
        "exit /b 0",
        ":fail",
        "echo.",
        "echo  Something failed to download. Check your connection and run this file again.",
        "pause",
        "exit /b 1", ""])
    (ASSETS / "GSCraft-Setup.cmd").write_bytes(cmd.encode("ascii"))
    total = sum(p.stat().st_size for p in ASSETS.iterdir())
    print(f"packwiz pack: {hosted} Modrinth-hosted jars, {missing} release-hosted jars, {len(plain)} plain files -> {OUT}")
    print(f"assets: {len(list(ASSETS.iterdir()))} files, {total/1e6:.1f} MB -> {ASSETS}")


if __name__ == "__main__":
    main()
