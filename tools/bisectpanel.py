#!/usr/bin/env python3
"""
bisectpanel.py - command-line client for the BisectHosting games panel (Pterodactyl "Starbase").

The API token is read from a local config file and never passed on the command line,
so it never lands in shell history.

Setup:
    python bisectpanel.py init          # writes the config template and opens it in Notepad

Usage:
    python bisectpanel.py servers                   # list servers you can see (finds your server id)
    python bisectpanel.py resources                 # state, CPU, memory, disk, uptime
    python bisectpanel.py ls /mods                  # list a directory
    python bisectpanel.py cat /server.properties    # print a text file
    python bisectpanel.py get /server.properties    # download one file into ./pull
    python bisectpanel.py cmd "list"                # send a console command
    python bisectpanel.py audit                     # pull the whole review set into ./pull
    python bisectpanel.py pullmods keep.txt build/mods  # copy named jars off the server, with SHA-256
    python bisectpanel.py put local.jar /mods       # upload one file into a server directory
    python bisectpanel.py rm /config /logs          # delete paths (refuses libraries, forge jar, eula)
    python bisectpanel.py mkdir /kubejs/server_scripts
    python bisectpanel.py power restart             # start | stop | restart | kill
    python bisectpanel.py pull /world              # compress a remote dir, download it, verify zip
    python bisectpanel.py backup create|list|wait <uuid>|download <uuid>
    python bisectpanel.py mv /mods /mods_old        # rename within a directory
    python bisectpanel.py setvar AIKARS_ENABLED 1  # startup (egg) variable
    python bisectpanel.py putdir build/phase02 /mods  # upload every file in a folder

Config file: %USERPROFILE%\\.bisect\\config.json
"""

import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

CONFIG_DIR = Path(os.path.expanduser("~")) / ".bisect"
CONFIG_PATH = CONFIG_DIR / "config.json"
DEFAULT_PANEL = "https://games.bisecthosting.com"
# Bisect sits behind Cloudflare, which returns error 1010 for the default
# Python-urllib signature. A browser-style UA clears it.
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/128.0 Safari/537.36 bisectpanel/1.0")
OUT_DIR = Path.cwd() / "pull"

TEMPLATE = {
    "panel": DEFAULT_PANEL,
    "token": "PASTE_YOUR_ptlc_KEY_HERE",
    "server": "PASTE_YOUR_SERVER_ID_HERE",
}


# --------------------------------------------------------------------------- config


def cmd_init() -> int:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_PATH.exists():
        print(f"Config already exists: {CONFIG_PATH}")
    else:
        CONFIG_PATH.write_text(json.dumps(TEMPLATE, indent=2), encoding="utf-8")
        print(f"Wrote template: {CONFIG_PATH}")
    print()
    print("1. Generate a key in the panel: Account Settings -> Account -> API Credentials.")
    print("   Copy it immediately; the panel will not show it again. It starts with 'ptlc_'.")
    print("2. Paste it into the file that just opened, next to \"token\", and save.")
    print("3. Leave \"server\" as-is for now, then run:  python bisectpanel.py servers")
    print("   That prints your server id. Paste it next to \"server\" and save again.")
    try:
        subprocess.Popen(["notepad.exe", str(CONFIG_PATH)])
    except OSError:
        print(f"\n(Open it yourself: {CONFIG_PATH})")
    return 0


def load_config(require_server: bool = True) -> dict:
    if not CONFIG_PATH.exists():
        sys.exit(f"No config found. Run first:  python {Path(__file__).name} init")
    try:
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.exit(f"Config is not valid JSON ({exc}). Fix or delete {CONFIG_PATH} and re-run init.")

    token = str(cfg.get("token", "")).strip()
    if not token or token == TEMPLATE["token"]:
        sys.exit(f"No API token set yet. Paste your ptlc_ key into {CONFIG_PATH}")
    if not token.startswith("ptlc_"):
        print("Warning: client API keys normally start with 'ptlc_'. An 'ptla_' key is an "
              "application key and will not work for these endpoints.", file=sys.stderr)

    cfg["panel"] = str(cfg.get("panel") or DEFAULT_PANEL).rstrip("/")
    server = str(cfg.get("server", "")).strip()
    if require_server and (not server or server == TEMPLATE["server"]):
        sys.exit("No server id set yet. Run 'python bisectpanel.py servers', then paste the id "
                 f"into {CONFIG_PATH}")
    cfg["server"] = server
    return cfg


# --------------------------------------------------------------------------- transport


def request(cfg: dict, method: str, path: str, params: dict | None = None,
            body: dict | None = None, raw: bool = False):
    url = f"{cfg['panel']}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {
        "Authorization": f"Bearer {cfg['token']}",
        "Accept": "Application/vnd.pterodactyl.v1+json",
        "User-Agent": USER_AGENT,
    }
    if data is not None:
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = resp.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:500]
        hint = ""
        if exc.code in (401, 403):
            hint = "  (bad or expired token, or the key's allowed-IP list excludes this machine)"
        elif exc.code == 404:
            hint = "  (wrong server id, or the file/path does not exist)"
        sys.exit(f"HTTP {exc.code} on {method} {path}{hint}\n{detail}")
    except urllib.error.URLError as exc:
        sys.exit(f"Could not reach {cfg['panel']}: {exc.reason}")

    if raw:
        return payload
    if not payload:
        return None
    return json.loads(payload.decode("utf-8"))


def fetch_signed(url: str) -> bytes:
    """Pterodactyl hands back a one-time signed URL; it takes no auth header."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        sys.exit(f"HTTP {exc.code} fetching signed download URL - the node's daemon is "
                 "unhealthy or the file vanished. Retry in a minute.")
    except urllib.error.URLError as exc:
        sys.exit(f"Could not fetch signed download URL: {exc.reason}")


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024 or unit == "GB":
            return f"{n:,.1f} {unit}" if unit != "B" else f"{int(n)} B"
        n /= 1024
    return f"{n:.1f} GB"


# --------------------------------------------------------------------------- commands


def cmd_servers() -> int:
    cfg = load_config(require_server=False)
    data = request(cfg, "GET", "/api/client")
    rows = data.get("data", []) if data else []
    if not rows:
        print("No servers visible to this key.")
        return 1
    print(f"{'SERVER ID':<12}  {'NAME':<34}  NODE")
    print("-" * 74)
    for row in rows:
        a = row.get("attributes", {})
        print(f"{a.get('identifier',''):<12}  {str(a.get('name',''))[:34]:<34}  {a.get('node','')}")
    print("\nPaste the SERVER ID you want into", CONFIG_PATH)
    return 0


def cmd_resources() -> int:
    cfg = load_config()
    data = request(cfg, "GET", f"/api/client/servers/{cfg['server']}/resources")
    a = (data or {}).get("attributes", {})
    r = a.get("resources", {})
    print(f"state       {a.get('current_state','?')}")
    print(f"uptime      {r.get('uptime',0) / 1000 / 60:,.0f} min")
    print(f"memory      {human(r.get('memory_bytes', 0))}")
    print(f"cpu         {r.get('cpu_absolute', 0):.1f} %")
    print(f"disk        {human(r.get('disk_bytes', 0))}")
    return 0


def cmd_ls(directory: str) -> int:
    cfg = load_config()
    data = request(cfg, "GET", f"/api/client/servers/{cfg['server']}/files/list",
                   params={"directory": directory})
    rows = (data or {}).get("data", [])
    if not rows:
        print(f"(empty or not a directory: {directory})")
        return 0
    rows.sort(key=lambda r: (not r["attributes"].get("is_file", True),
                             r["attributes"].get("name", "")))
    total = 0
    for row in rows:
        a = row["attributes"]
        size = a.get("size", 0)
        total += size if a.get("is_file") else 0
        kind = "     <DIR>" if not a.get("is_file") else f"{human(size):>10}"
        print(f"{kind}  {a.get('modified_at','')[:10]}  {a.get('name','')}")
    print(f"\n{len(rows)} entries, {human(total)} of files in {directory}")
    return 0


def cmd_cat(remote: str) -> int:
    cfg = load_config()
    path = f"/api/client/servers/{cfg['server']}/files/contents"
    # Bisect's customised panel exposes this as POST (stock Pterodactyl uses GET).
    try:
        body = request(cfg, "POST", path, params={"file": remote}, raw=True)
    except SystemExit:
        # Fall back to the signed-download route, which is known to work.
        data = request(cfg, "GET", f"/api/client/servers/{cfg['server']}/files/download",
                       params={"file": remote})
        url = (data or {}).get("attributes", {}).get("url")
        if not url:
            sys.exit(f"Could not read {remote}")
        body = fetch_signed(url)
    sys.stdout.write(body.decode("utf-8", "replace"))
    return 0


def cmd_info() -> int:
    """Allocation limits, docker image (=> Java), SFTP endpoint, startup invocation."""
    cfg = load_config()
    data = request(cfg, "GET", f"/api/client/servers/{cfg['server']}")
    a = (data or {}).get("attributes", {})
    lim = a.get("limits", {})
    print(f"name         {a.get('name')}")
    print(f"node         {a.get('node')}")
    print(f"memory limit {lim.get('memory')} MB")
    print(f"disk limit   {lim.get('disk')} MB")
    print(f"cpu limit    {lim.get('cpu')} %")
    print(f"docker image {a.get('docker_image')}")
    print(f"invocation   {a.get('invocation')}")
    sftp = a.get("sftp_details", {})
    print(f"sftp         {sftp.get('ip')}:{sftp.get('port')}")
    return 0


def cmd_startup() -> int:
    """Startup command and egg variables (loader / MC version live here)."""
    cfg = load_config()
    data = request(cfg, "GET", f"/api/client/servers/{cfg['server']}/startup")
    meta = (data or {}).get("meta", {})
    print(f"startup      {meta.get('startup_command')}")
    print(f"raw          {meta.get('raw_startup_command')}")
    print("variables:")
    for row in (data or {}).get("data", []):
        v = row.get("attributes", {})
        print(f"  {v.get('env_variable'):<28} = {v.get('server_value')!r:<40} ({v.get('name')})")
    return 0


def download(cfg: dict, remote: str, dest: Path) -> Path:
    data = request(cfg, "GET", f"/api/client/servers/{cfg['server']}/files/download",
                   params={"file": remote})
    url = (data or {}).get("attributes", {}).get("url")
    if not url:
        sys.exit(f"Panel returned no download URL for {remote}")
    blob = fetch_signed(url)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(blob)
    return dest


def cmd_get(remote: str, dest: str | None) -> int:
    cfg = load_config()
    target = Path(dest) if dest else OUT_DIR / Path(remote).name
    download(cfg, remote, target)
    print(f"{human(target.stat().st_size)}  ->  {target}")
    return 0


def cmd_cmd(command: str) -> int:
    cfg = load_config()
    request(cfg, "POST", f"/api/client/servers/{cfg['server']}/command",
            body={"command": command})
    print(f"sent: {command}")
    print("Output appears in the panel console; this endpoint returns no response body.")
    return 0


def _zip_ok(path: Path) -> bool:
    """True if the archive is a ZIP whose every member passes its CRC.
    Bisect's compress endpoint produces ZIP (PK magic) regardless of extension."""
    import zipfile
    try:
        with zipfile.ZipFile(path) as z:
            return z.testzip() is None
    except zipfile.BadZipFile:
        return False


def cmd_audit() -> int:
    """Pull everything the server review needs, in as few requests as possible."""
    cfg = load_config()
    sid = cfg["server"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Plain-text files worth having verbatim.
    for remote in ("/server.properties", "/ops.json", "/whitelist.json",
                   "/eula.txt", "/logs/latest.log"):
        try:
            download(cfg, remote, OUT_DIR / Path(remote).name)
            print(f"  got {remote}")
        except SystemExit as exc:
            print(f"  skip {remote}  ({exc})")

    # 2. The mods listing - filenames carry the version strings.
    listing = request(cfg, "GET", f"/api/client/servers/{sid}/files/list",
                      params={"directory": "/mods"})
    rows = (listing or {}).get("data", [])
    manifest = OUT_DIR / "mods-listing.txt"
    with manifest.open("w", encoding="utf-8") as fh:
        for row in sorted(rows, key=lambda r: r["attributes"].get("name", "")):
            a = row["attributes"]
            fh.write(f"{a.get('size',0):>12}  {a.get('modified_at','')[:10]}  {a.get('name','')}\n")
    print(f"  got /mods listing ({len(rows)} entries) -> {manifest.name}")

    # 3. Archive the bulky directories server-side, then pull one file each.
    for root, targets, label in (
        ("/", ["config"], "config"),
        ("/", ["crash-reports"], "crash-reports"),
        ("/", ["logs"], "logs"),
        ("/", ["kubejs"], "kubejs"),
        ("/", ["defaultconfigs"], "defaultconfigs"),
    ):
        try:
            made = request(cfg, "POST", f"/api/client/servers/{sid}/files/compress",
                           body={"root": root, "files": targets})
            name = (made or {}).get("attributes", {}).get("name")
            if not name:
                print(f"  skip {label} (no archive returned)")
                continue
            dest = download(cfg, f"/{name}", OUT_DIR / f"{label}.zip")
            ok = _zip_ok(dest)
            print(f"  {'got' if ok else 'CORRUPT'} {label}  {human(dest.stat().st_size)}"
                  + ("" if ok else "  <- re-run audit when the daemon is healthy"))
            request(cfg, "POST", f"/api/client/servers/{sid}/files/delete",
                    body={"root": "/", "files": [name]})
        except SystemExit as exc:
            print(f"  skip {label}  ({exc})")

    print(f"\nDone. Everything is in {OUT_DIR}")
    return 0



# --------------------------------------------------------------------------- write side


def _multipart(field: str, filename: str, blob: bytes) -> tuple[bytes, str]:
    boundary = "----bisectpanel" + os.urandom(8).hex()
    head = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{field}"; filename="{filename}"\r\n'
        "Content-Type: application/octet-stream\r\n\r\n"
    ).encode()
    tail = f"\r\n--{boundary}--\r\n".encode()
    return head + blob + tail, f"multipart/form-data; boundary={boundary}"


def cmd_put(local: str, remote_dir: str) -> int:
    """Upload one local file into a server directory via the panel's signed upload URL."""
    cfg = load_config()
    src = Path(local)
    if not src.is_file():
        sys.exit(f"Not a file: {src}")
    data = request(cfg, "GET", f"/api/client/servers/{cfg['server']}/files/upload")
    url = (data or {}).get("attributes", {}).get("url")
    if not url:
        sys.exit("Panel returned no upload URL")
    url += ("&" if "?" in url else "?") + urllib.parse.urlencode({"directory": remote_dir})
    body, ctype = _multipart("files", src.name, src.read_bytes())
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"Content-Type": ctype, "User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            resp.read()
    except urllib.error.HTTPError as exc:
        sys.exit(f"HTTP {exc.code} uploading {src.name}: "
                 f"{exc.read().decode('utf-8', 'replace')[:300]}")
    print(f"{human(src.stat().st_size)}  {src.name}  ->  {remote_dir}")
    return 0


def cmd_rm(paths: list[str]) -> int:
    """Delete files or folders. Refuses the paths the rebuild must never touch."""
    cfg = load_config()
    protected = {"/", "/libraries", "/eula.txt", "/server.properties"}
    for pth in paths:
        norm = "/" + pth.strip("/")
        if norm in protected or (norm.startswith("/forge-") and norm.endswith(".jar")):
            sys.exit(f"Refusing to delete protected path {norm}")
    request(cfg, "POST", f"/api/client/servers/{cfg['server']}/files/delete",
            body={"root": "/", "files": [pth.strip("/") for pth in paths]})
    print("deleted:", ", ".join(paths))
    return 0


def cmd_mkdir(path: str) -> int:
    cfg = load_config()
    parent, _, name = path.rstrip("/").rpartition("/")
    request(cfg, "POST", f"/api/client/servers/{cfg['server']}/files/create-folder",
            body={"root": parent or "/", "name": name})
    print("created:", path)
    return 0


def cmd_power(signal: str) -> int:
    if signal not in ("start", "stop", "restart", "kill"):
        sys.exit("usage: bisectpanel.py power start|stop|restart|kill")
    cfg = load_config()
    request(cfg, "POST", f"/api/client/servers/{cfg['server']}/power", body={"signal": signal})
    print("sent power signal:", signal)
    return 0


def cmd_pullmods(listfile: str, dest_dir: str) -> int:
    """Download every jar named in listfile (one filename per line) from /mods into dest_dir,
    recording SHA-256 so the manifest can pin what was actually pulled."""
    import hashlib
    cfg = load_config()
    names = [ln.strip() for ln in Path(listfile).read_text(encoding="utf-8").splitlines()
             if ln.strip() and not ln.startswith("#")]
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    manifest = dest / "pulled.sha256"
    got, failed = 0, []
    with manifest.open("a", encoding="utf-8") as fh:
        for name in names:
            try:
                path = download(cfg, f"/mods/{name}", dest / name)
            except SystemExit as exc:
                failed.append(f"{name}: {exc}")
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            fh.write(f"{digest}  {name}\n")
            got += 1
            print(f"  {human(path.stat().st_size):>10}  {name}")
    print(f"\n{got}/{len(names)} pulled -> {dest}  (hashes in {manifest.name})")
    for f in failed:
        print("  FAILED", f)
    return 0 if not failed else 1


# --------------------------------------------------------------------------- backups and bulk pull


def _stream_signed(url: str, dest: Path) -> Path:
    """Stream a signed download URL to disk without holding it in memory."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(req, timeout=900) as resp, dest.open("wb") as fh:
            while chunk := resp.read(1 << 20):
                fh.write(chunk)
    except urllib.error.HTTPError as exc:
        sys.exit(f"HTTP {exc.code} streaming download: {exc.read().decode('utf-8', 'replace')[:300]}")
    return dest


def cmd_backup(args: list[str]) -> int:
    """backup list | create [name] | wait <uuid> | download <uuid> [dest]"""
    import time
    from datetime import datetime
    cfg = load_config()
    base = f"/api/client/servers/{cfg['server']}/backups"
    sub = args[0] if args else "list"

    if sub == "list":
        data = request(cfg, "GET", base)
        rows = (data or {}).get("data", [])
        if not rows:
            print("no backups")
            return 0
        for r in rows:
            a = r["attributes"]
            state = "done" if a.get("completed_at") else "in progress"
            if a.get("completed_at") and not a.get("is_successful", True):
                state = "FAILED"
            print(f"{a['uuid']}  {human(a.get('bytes', 0)):>10}  {state:<11}  "
                  f"{str(a.get('created_at', ''))[:19]}  {a.get('name', '')}")
        return 0

    if sub == "create":
        name = args[1] if len(args) > 1 else datetime.now().strftime("bisectpanel %Y-%m-%d %H%M")
        data = request(cfg, "POST", base, body={"name": name, "is_locked": False})
        a = (data or {}).get("attributes", {})
        print("backup started:", a.get("uuid"), "|", a.get("name"))
        print("poll with:  backup wait", a.get("uuid"))
        return 0

    if sub == "wait":
        if len(args) < 2:
            sys.exit("usage: backup wait <uuid>")
        uuid = args[1]
        for _ in range(180):  # up to 30 minutes
            data = request(cfg, "GET", f"{base}/{uuid}")
            a = (data or {}).get("attributes", {})
            if a.get("completed_at"):
                ok = a.get("is_successful", True)
                print(("done" if ok else "FAILED") + f"  {human(a.get('bytes', 0))}  {a.get('name')}")
                return 0 if ok else 1
            time.sleep(10)
        sys.exit("backup still not complete after 30 minutes")

    if sub == "download":
        if len(args) < 2:
            sys.exit("usage: backup download <uuid> [dest]")
        uuid = args[1]
        data = request(cfg, "GET", f"{base}/{uuid}/download")
        url = (data or {}).get("attributes", {}).get("url")
        if not url:
            sys.exit("no download URL returned")
        dest = Path(args[2]) if len(args) > 2 else OUT_DIR / f"backup-{uuid[:8]}.tar.gz"
        _stream_signed(url, dest)
        print(f"{human(dest.stat().st_size)}  ->  {dest}")
        return 0

    sys.exit("usage: backup list | create [name] | wait <uuid> | download <uuid> [dest]")


def cmd_pull(remote_dir: str, local_zip: str | None) -> int:
    """Compress a remote directory server-side, download the archive, remove it remotely,
    and verify the local file is a readable ZIP."""
    cfg = load_config()
    sid = cfg["server"]
    remote_dir = "/" + remote_dir.strip("/")
    parent, _, name = remote_dir.rpartition("/")
    parent = parent or "/"
    made = request(cfg, "POST", f"/api/client/servers/{sid}/files/compress",
                   body={"root": parent, "files": [name]})
    archive = (made or {}).get("attributes", {}).get("name")
    if not archive:
        sys.exit(f"compress returned no archive for {remote_dir}")
    remote_archive = f"{parent.rstrip('/')}/{archive}"
    dest = Path(local_zip) if local_zip else OUT_DIR / (name.replace(" ", "_") + ".zip")
    data = request(cfg, "GET", f"/api/client/servers/{sid}/files/download",
                   params={"file": remote_archive})
    url = (data or {}).get("attributes", {}).get("url")
    if not url:
        sys.exit(f"no download URL for {remote_archive}")
    _stream_signed(url, dest)
    request(cfg, "POST", f"/api/client/servers/{sid}/files/delete",
            body={"root": parent, "files": [archive]})
    ok = _zip_ok(dest)
    print(f"{'ok' if ok else 'CORRUPT'}  {human(dest.stat().st_size)}  {remote_dir}  ->  {dest}")
    return 0 if ok else 1


# --------------------------------------------------------------------------- rename and startup vars


def cmd_mv(src: str, dst: str) -> int:
    """Rename or move a file/folder on the server (both paths absolute, same as ls)."""
    cfg = load_config()
    s = "/" + src.strip("/"); d = "/" + dst.strip("/")
    sp, _, sname = s.rpartition("/"); dp, _, dname = d.rpartition("/")
    if (sp or "/") != (dp or "/"):
        sys.exit("mv within one directory only (the panel renames; it does not move across folders)")
    request(cfg, "PUT", f"/api/client/servers/{cfg['server']}/files/rename",
            body={"root": sp or "/", "files": [{"from": sname, "to": dname}]})
    print(f"renamed {s} -> {d}")
    return 0


def cmd_setvar(key: str, value: str) -> int:
    """Set a startup (egg) variable, e.g. AIKARS_ENABLED 1. Takes effect on next start."""
    cfg = load_config()
    data = request(cfg, "PUT", f"/api/client/servers/{cfg['server']}/startup/variable",
                   body={"key": key, "value": value})
    a = (data or {}).get("attributes", {})
    print(f"{a.get('env_variable', key)} = {a.get('server_value', value)!r}")
    return 0


def cmd_putdir(local_dir: str, remote_dir: str) -> int:
    """Upload every file in a local directory (non-recursive) into a remote directory."""
    files = sorted(p for p in Path(local_dir).iterdir() if p.is_file())
    if not files:
        sys.exit(f"nothing to upload in {local_dir}")
    failed = []
    for i, p in enumerate(files, 1):
        try:
            cmd_put(str(p), remote_dir)
        except SystemExit as exc:
            failed.append(f"{p.name}: {exc}")
        print(f"  [{i}/{len(files)}]")
    print(f"uploaded {len(files) - len(failed)}/{len(files)} into {remote_dir}")
    for f in failed:
        print("  FAILED", f)
    return 0 if not failed else 1

# --------------------------------------------------------------------------- entry


USAGE = __doc__


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in ("-h", "--help", "help"):
        print(USAGE)
        return 0
    verb, args = argv[1], argv[2:]

    # Git Bash (MSYS) rewrites arguments that look like POSIX paths into Windows paths
    # before Python ever sees them: "/mods" becomes "C:/Program Files/Git/mods". That
    # silently turns a remote path into one the panel cannot serve, and the panel answers
    # with a misleading DaemonConnectionException. Refuse loudly instead.
    REMOTE_PATH_VERBS = {"ls", "cat", "get", "rm", "mkdir", "pull", "mv"}
    if verb in REMOTE_PATH_VERBS:
        suspects = args[:1] if verb == "get" else args
        for a in suspects:
            if len(a) > 2 and a[1] == ":" and a[2] in "/\\":
                sys.exit("Remote path was rewritten by Git Bash into a Windows path: "
                         + repr(a) + ". Run with MSYS_NO_PATHCONV=1, or use PowerShell/cmd.")

    if verb == "init":
        return cmd_init()
    if verb == "servers":
        return cmd_servers()
    if verb == "resources":
        return cmd_resources()
    if verb == "info":
        return cmd_info()
    if verb == "startup":
        return cmd_startup()
    if verb == "audit":
        return cmd_audit()
    if verb == "ls":
        return cmd_ls(args[0] if args else "/")
    if verb == "cat":
        if not args:
            sys.exit("usage: bisectpanel.py cat <remote path>")
        return cmd_cat(args[0])
    if verb == "get":
        if not args:
            sys.exit("usage: bisectpanel.py get <remote path> [local path]")
        return cmd_get(args[0], args[1] if len(args) > 1 else None)
    if verb == "put":
        if len(args) < 2:
            sys.exit("usage: bisectpanel.py put <local file> <remote dir>")
        return cmd_put(args[0], args[1])
    if verb == "rm":
        if not args:
            sys.exit("usage: bisectpanel.py rm <remote path> [...]")
        return cmd_rm(args)
    if verb == "mkdir":
        if not args:
            sys.exit("usage: bisectpanel.py mkdir <remote path>")
        return cmd_mkdir(args[0])
    if verb == "power":
        return cmd_power(args[0] if args else "")
    if verb == "pullmods":
        if len(args) < 2:
            sys.exit("usage: bisectpanel.py pullmods <list.txt> <local dir>")
        return cmd_pullmods(args[0], args[1])
    if verb == "backup":
        return cmd_backup(args)
    if verb == "pull":
        if not args:
            sys.exit("usage: bisectpanel.py pull <remote dir> [local zip]")
        return cmd_pull(args[0], args[1] if len(args) > 1 else None)
    if verb == "mv":
        if len(args) < 2:
            sys.exit("usage: bisectpanel.py mv <remote from> <remote to>")
        return cmd_mv(args[0], args[1])
    if verb == "setvar":
        if len(args) < 2:
            sys.exit("usage: bisectpanel.py setvar <KEY> <value>")
        return cmd_setvar(args[0], args[1])
    if verb == "putdir":
        if len(args) < 2:
            sys.exit("usage: bisectpanel.py putdir <local dir> <remote dir>")
        return cmd_putdir(args[0], args[1])
    if verb == "cmd":
        if not args:
            sys.exit('usage: bisectpanel.py cmd "<console command>"')
        return cmd_cmd(" ".join(args))

    sys.exit(f"Unknown command '{verb}'. Run with --help for usage.")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
