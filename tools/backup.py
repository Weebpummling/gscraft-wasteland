"""Full local backup of the server: every top-level entry of the server root, directories as
verified ZIPs (compressed server-side), files as-is, into <dest>\\<YYYY-MM-DD>\\.

usage: backup.py <dest root> [--skip name,name]
"""
import subprocess, sys, time, json, re
from pathlib import Path

HERE = Path(__file__).parent


def panel(*a):
    r = subprocess.run([sys.executable, str(HERE / "bisectpanel.py"), *a], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def main(argv):
    dest = Path(argv[1]) / time.strftime("%Y-%m-%d"); dest.mkdir(parents=True, exist_ok=True)
    skip = set(argv[argv.index("--skip") + 1].split(",")) if "--skip" in argv else set()
    rc, out = panel("ls", "/")
    entries = []
    for ln in out.splitlines():
        m = re.match(r"\s*(<DIR>|[\d.]+\s*[KMG]?B)\s+\S+\s+(.+?)\s*$", ln)
        if m: entries.append((m.group(1) == "<DIR>", m.group(2)))
    print(f"{len(entries)} root entries -> {dest}", flush=True)
    log = []
    t0 = time.time()
    for is_dir, name in entries:
        if name in skip: print("skip", name, flush=True); continue
        t = time.time()
        if not re.fullmatch(r"[\w .\-]+", name):
            print("skip odd name", repr(name), flush=True); continue
        if is_dir:
            rc, o = panel("pull", "/" + name)          # tool picks pull\<name>.zip (its guard rejects drive-letter args)
            produced = HERE / "pull" / (name.replace(" ", "_") + ".zip")
            target = dest / (name + ".zip")
            if produced.exists(): produced.replace(target)
        else:
            rc, o = panel("get", "/" + name)
            produced = HERE / "pull" / name
            target = dest / name
            if produced.exists(): produced.replace(target)
        ok = rc == 0 and target.exists()
        size = target.stat().st_size if target.exists() else 0
        print(f"{'ok ' if ok else 'FAIL'} {size/1e6:8.1f} MB  {name}  ({int(time.time()-t)} s)", flush=True)
        if not ok: print("   ", o.strip().splitlines()[-1] if o.strip() else "", flush=True)
        log.append({"name": name, "dir": is_dir, "ok": ok, "bytes": size})
    json.dump(log, open(dest / "backup-manifest.json", "w"), indent=1)
    total = sum(e["bytes"] for e in log); bad = [e["name"] for e in log if not e["ok"]]
    print(f"BACKUP DONE: {len(log)} entries, {total/1e9:.2f} GB, {int(time.time()-t0)} s, failures: {bad}", flush=True)


if __name__ == "__main__":
    main(sys.argv)
