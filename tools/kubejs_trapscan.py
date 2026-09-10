"""Scan GSCraft's KubeJS scripts for the traps verified on KubeJS 2001.6.5-build.26 / Rhino 2001.2.3-build.10.
Reference and evidence: docs/notes/gscraft-kubejs-traps.md. Run it before any KubeJS script ships.

    python tools/kubejs_trapscan.py                 every copy: server, repo build, packwiz, client instance
    python tools/kubejs_trapscan.py FILE [FILE...]  just these files

Comments and string literals are blanked first (line numbers kept), then braces are walked with each `{`
classified as a function body, a statement block or an object literal, so a rule can depend on where a
declaration sits rather than on a word appearing nearby.

Rules (sections of the trap note):
  CONST_BLOCK_THROWS   const inside a nested block of a function that has a try, a nested function or uses
                       `arguments`: throws "redeclaration of var" whenever the line runs            (2.1)
  CONST_LOOP_STALE     const inside a loop body of a function with none of those: keeps its first value (2.1)
  CONST_BLOCK_FRAGILE  const inside another block of such a function: breaks when a try/closure is added (2.1)
  CANCEL_IN_TRY        KubeJS cancel()/success()/exit() inside a try: a JS catch swallows it             (2.2)
  FORGE_UNGUARDED      ForgeEvents handler with no try at its top level: an escaped throw crashes      (1.2)
  STARTUP_CONSOLE_ERROR console.error in a startup script: at load time it blocks a dedicated boot     (1.1)
  COMMENT_PROPERTY     a // line read as a script property (priority / ignore / ignored / packmode / requires) (2.7)
  MATH_FIELD           Math.PI / Math.E and the other constants are undefined                          (2.4)
  SERVER_LEVELS        server.levels is undefined; use server.getAllLevels()                            (4)
  CHECKSPAWN           checkSpawn: cancel() does not block, success() does; silent for NBT summons and
                       createEntity + spawn()                                                           (2.3)
  SYNTAX               spread, default parameters, class                                                (3)
  DUP_TOPLEVEL         one top-level name in two files of one script type (shared scope)               (2.5)

Exit status is 1 when a rule that breaks behaviour today fires (everything except CONST_BLOCK_FRAGILE,
CHECKSPAWN and handler-time STARTUP_CONSOLE_ERROR, which are warnings).
"""
import collections
import re
import sys
from pathlib import Path

ROOTS = {
    "server": Path(r"G:/GSCraft/server/kubejs"),
    "repo-build": Path(__file__).resolve().parent.parent / "build" / "kubejs",
    "packwiz": Path(__file__).resolve().parent.parent / "build" / "packwiz" / "kubejs",
    "client": Path(r"G:/GSCraft/client/instances/GSCraft/.minecraft/kubejs"),
}
EXTRA = [Path(__file__).resolve().parent / "kubejs_equipment_dump.js"]
PROPERTY_KEYS = {"priority", "ignore", "ignored", "packmode", "requires"}
CONTROL = {"if", "for", "while", "switch", "catch", "with"}
LOOPS = {"for", "while", "do"}
WARNINGS = {"CONST_BLOCK_FRAGILE", "CHECKSPAWN", "STARTUP_CONSOLE_ERROR_HANDLER"}


def strip(src):
    out, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        nxt = src[i + 1] if i + 1 < n else ""
        if c == "/" and nxt == "/":
            j = src.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif c == "/" and nxt == "*":
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append("".join(ch if ch == "\n" else " " for ch in src[i:j]))
            i = j
        elif c in "'\"`":
            j = i + 1
            while j < n and src[j] != c:
                j += 2 if src[j] == "\\" else 1
            j = min(j + 1, n)
            out.append(c + "".join(ch if ch == "\n" else " " for ch in src[i + 1:j - 1]) + c)
            i = j
        else:
            out.append(c)
            i += 1
    return "".join(out)


class Frame:
    def __init__(self, kind, opener, parent):
        self.kind, self.opener, self.parent = kind, opener, parent      # func | block | obj | top
        self.has_try = self.has_nested = self.uses_arguments = False


def enclosing_func(frame):
    f = frame
    while f.kind not in ("func", "top"):
        f = f.parent
    return f


def scan_file(path, script_kind):
    raw = path.read_text(encoding="utf-8", errors="replace")
    code = strip(raw)
    raw_lines = raw.splitlines()
    findings = []

    def add(kind, where, note, is_line=False):
        ln = where if is_line else code.count("\n", 0, where) + 1
        src = raw_lines[ln - 1].strip() if 0 < ln <= len(raw_lines) else ""
        findings.append((kind, ln, note, src[:110]))

    toks = [(m.start(), m.group(0)) for m in re.finditer(r"=>|\|\||&&|[A-Za-z_$][\w$]*|[{}()\[\];,:=?.]", code)]
    top = Frame("top", None, None)
    top.has_nested = True            # every script body holds handler functions
    stack = [top]
    consts, cancels, errors = [], [], []
    parens, for_headers = [], []

    for idx, (pos, tok) in enumerate(toks):
        prev = toks[idx - 1][1] if idx else ""
        if tok == "(":
            parens.append(prev)
            if prev == "for":
                for_headers.append(len(parens))
        elif tok == ")":
            if for_headers and for_headers[-1] == len(parens):
                for_headers.pop()
            if parens:
                parens.pop()
        elif tok == "{":
            if prev == "=>":
                kind, opener = "func", "=>"
            elif prev == ")":
                d, k = 0, idx - 1
                while k >= 0:
                    t = toks[k][1]
                    if t == ")":
                        d += 1
                    elif t == "(":
                        d -= 1
                        if d == 0:
                            break
                    k -= 1
                before = toks[k - 1][1] if k > 0 else ""
                before2 = toks[k - 2][1] if k > 1 else ""
                if before in CONTROL:
                    kind, opener = "block", before
                elif before == "function" or before2 == "function":
                    kind, opener = "func", "function"
                else:
                    kind, opener = "block", before
            elif prev in ("try", "else", "finally", "do"):
                kind, opener = "block", prev
            elif prev in ("=", "(", ",", ":", "[", "?", "return", "", "||", "&&"):
                kind, opener = "obj", prev
            else:
                kind, opener = "block", prev
            fr = Frame(kind, opener, stack[-1])
            if kind == "func":
                enclosing_func(stack[-1]).has_nested = True
            if kind == "block" and opener == "try":
                enclosing_func(stack[-1]).has_try = True
            stack.append(fr)
        elif tok == "}":
            if len(stack) > 1:
                stack.pop()
        elif tok == "arguments":
            enclosing_func(stack[-1]).uses_arguments = True
        elif tok == "const" and not for_headers:
            consts.append((pos, stack[-1]))
        elif tok in ("cancel", "success", "exit") and prev == "." and idx + 1 < len(toks) and toks[idx + 1][1] == "(":
            cancels.append((pos, stack[-1]))
        elif tok == "error" and prev == "." and idx >= 2 and toks[idx - 2][1] == "console":
            errors.append((pos, stack[-1]))

    for pos, frame in consts:
        chain, f = [], frame
        while f.kind not in ("func", "top"):
            if f.kind == "block":
                chain.append(f)
            f = f.parent
        if not chain:
            continue
        if f.has_try or f.has_nested or f.uses_arguments:
            add("CONST_BLOCK_THROWS", pos, "throws 'redeclaration of var' whenever this line runs")
        elif any(b.opener in LOOPS for b in chain):
            add("CONST_LOOP_STALE", pos, "keeps its first value on later loop iterations, silently")
        else:
            add("CONST_BLOCK_FRAGILE", pos, "works only while this function has no try or closure; use var or let")

    for pos, frame in cancels:
        f, in_try = frame, False
        while f.kind not in ("func", "top"):
            if f.kind == "block" and f.opener == "try":
                in_try = True
            f = f.parent
        if in_try:
            add("CANCEL_IN_TRY", pos, "cancel()/success()/exit() throw internally; the catch swallows them")

    if script_kind.startswith("startup"):
        for pos, frame in errors:
            if enclosing_func(frame).kind == "top":
                add("STARTUP_CONSOLE_ERROR", pos, "console.error at load time blocks a dedicated server's boot; use console.warn")
            else:
                add("STARTUP_CONSOLE_ERROR_HANDLER", pos, "prefer console.warn in startup scripts (runtime effect unverified)")

    for m in re.finditer(r"ForgeEvents\.on(Generic)?Event\s*\(", code):
        start = code.find("{", m.end())
        if start < 0:
            continue
        d, j = 0, start
        while j < len(code):
            if code[j] == "{":
                d += 1
            elif code[j] == "}":
                d -= 1
                if d == 0:
                    break
            j += 1
        flat, dd = [], 0
        for ch in code[start + 1:j]:
            if ch == "{":
                dd += 1
            elif ch == "}":
                dd -= 1
            elif dd == 0:
                flat.append(ch)
        if not re.search(r"\btry\b", "".join(flat)):
            add("FORGE_UNGUARDED", m.start(), "no try at handler top level: an escaped throw crashes the server")

    for i, line in enumerate(raw_lines, 1):
        t = line.strip()
        if t.startswith("//"):
            pm = re.match(r"^(\w+)\s*[:=]?\s*(-?\w+)$", t[2:].strip())
            if pm and pm.group(1).lower() in PROPERTY_KEYS:
                ok = pm.group(1).lower() == "priority" and re.fullmatch(r"-?\d+", pm.group(2))
                if not ok:
                    add("COMMENT_PROPERTY", i, f"read as script property {pm.group(1)}={pm.group(2)}", is_line=True)

    for m in re.finditer(r"\bMath\.(PI|E|LN2|LN10|LOG2E|LOG10E|SQRT1_2|SQRT2)\b", code):
        add("MATH_FIELD", m.start(), f"Math.{m.group(1)} is undefined in this Rhino")
    for m in re.finditer(r"\.levels\b", code):
        add("SERVER_LEVELS", m.start(), "server.levels is undefined; use server.getAllLevels()")
    for m in re.finditer(r"EntityEvents\.checkSpawn\b", code):
        add("CHECKSPAWN", m.start(), "cancel() does not block, success() does; silent for NBT summons and createEntity+spawn")
    for m in re.finditer(r"\.\.\.[A-Za-z_$\[]", code):
        add("SYNTAX", m.start(), "spread is a syntax error")
    for m in re.finditer(r"\bclass\s+[A-Za-z_$]", code):
        add("SYNTAX", m.start(), "class is a reserved word")
    for m in re.finditer(r"function\s*[\w$]*\s*\([^)]*=", code):
        add("SYNTAX", m.start(), "default parameters are a syntax error")

    tops = [(m.group(2), m.group(1)) for m in re.finditer(r"^(const|let|var|function)\s+([A-Za-z_$][\w$]*)", code, re.M)]
    return findings, tops


def main(argv):
    total = collections.Counter()

    def emit(prefix, name, k, ln, note, src):
        total[k] += 1
        print(f"{prefix}{name}:{ln:<4d} {k:30s} {note}\n{'':8s}| {src}")

    if len(argv) > 1:
        for a in argv[1:]:
            f = Path(a)
            kind = "startup_scripts" if "startup" in str(f) else "server_scripts"
            for k, ln, note, src in scan_file(f, kind)[0]:
                emit("", f.name, k, ln, note, src)
    else:
        for label, root in ROOTS.items():
            for kind in ("startup_scripts", "server_scripts"):
                d = root / kind
                if not d.exists():
                    continue
                names = collections.defaultdict(list)
                for f in sorted(d.rglob("*.js")):
                    if f.name == "example.js":
                        continue
                    findings, tops = scan_file(f, kind)
                    for n, k in tops:
                        names[n].append((f.name, k))
                    for k, ln, note, src in findings:
                        emit(f"{label:10s} {kind[:7]:7s} ", f.name, k, ln, note, src)
                for n, v in sorted(names.items()):
                    if len({x[0] for x in v}) > 1:
                        kinds = {x[1] for x in v}
                        sev = "load error (const/let)" if kinds & {"const", "let"} else "last-loaded definition wins for every file"
                        total["DUP_TOPLEVEL"] += 1
                        print(f"{label:10s} {kind[:7]:7s} (shared scope)  DUP_TOPLEVEL  '{n}' in "
                              + ", ".join(sorted({x[0] for x in v})) + f" -> {sev}")
        for f in EXTRA:
            if f.exists():
                for k, ln, note, src in scan_file(f, "server_scripts")[0]:
                    emit("tools      ", f.name, k, ln, note, src)
    print("\nTOTALS:", dict(total) if total else "clean")
    return 1 if any(k not in WARNINGS for k in total) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
