"""Apply the post-root-listing corrections to the audit and blueprint pages."""
import pathlib
import re
from html.parser import HTMLParser

SP = pathlib.Path(__file__).parent


def balanced(s: str) -> bool:
    class P(HTMLParser):
        VOID = {"br", "img", "meta", "link", "hr", "input"}

        def __init__(self):
            super().__init__()
            self.st, self.err = [], []

        def handle_starttag(self, t, a):
            if t not in self.VOID:
                self.st.append(t)

        def handle_endtag(self, t):
            if t in self.VOID:
                return
            if self.st and self.st[-1] == t:
                self.st.pop()
            else:
                self.err.append(t)
    q = P()
    q.feed(s)
    return not q.err and not q.st


def must_replace(s: str, old: str, new: str) -> str:
    assert s.count(old) == 1, old[:70]
    return s.replace(old, new, 1)


# ------------------------------------------------------------------ audit body
body_path = SP / "gscraft-audit-body.html"
b = body_path.read_text(encoding="utf-8")

# 1. Botania/liquidburner attribution line in "Lower-impact defects".
b = must_replace(
    b,
    "Their source is unattributed — the world's datapack folder could not be listed (see coverage below).",
    "Their source is a jar, not a datapack — the world's six datapacks are unrelated (see below) — and remains unattributed; it does not survive the rebuild either way.",
)

# 2. New subsection after the config-leftovers list: the server root.
root_section = """
  <h3>The server root is littered the same way</h3>
  <ul>
    <li><strong>Two world folders.</strong> <code>Escape From Minenkrafte</code> is the live world; <code>Escape From Minecraft</code> (December 2025) is a remnant of an earlier one — 21 entries, mostly stats and server config.</li>
    <li><strong>A stray <code>region/</code> at the root</strong> holding sixteen <code>.mca</code> files from October 2025, plus a stray <code>world/</code> and a stray <code>serverconfig/create-server.toml</code>. Someone unpacked a world in the wrong place.</li>
    <li><strong>A 531 MB zip</strong> (<code>73160fed-…</code>, September 2025) sitting in the root — an old upload or backup that was never removed. It is the single largest object on the server.</li>
    <li><code>mods alternate/</code> (empty) and <code>tacz_backup/</code> (empty) — abandoned stashes.</li>
    <li><strong>Four of the live world's six datapacks are 1.21 builds</strong> — AFK Announcer, Show Dimension In Name, Sleep, and Farmer's Delight cutting recipes for Twilight Forest, all tagged <code>[1.21]</code> on a 1.20.1 server. The other two are No More Phantoms and a Superb Warfare uniform pack.</li>
    <li><code>hs_err_pid123.log</code> from <strong>10 June 2026</strong>: a hard JVM crash (SIGSEGV) twenty seconds into boot. The stack is Spark's async profiler sampling the server thread during class loading — a profiler session had been left running across a restart, and the JVM race that triggers is a known one on that Java build. Not a mod fault; a reason never to leave <code>/spark profiler</code> running unattended.</li>
  </ul>
"""
b = must_replace(
    b,
    "    <li><strong>The Hordes config folder is from Hordes 1.6.0 for Minecraft 1.21</strong>",
    "    <li><strong>The Hordes config folder is from Hordes 1.6.0 for Minecraft 1.21</strong>",
)
anchor = "The mod falls back to its default table.</li>\n  </ul>\n</section>"
b = must_replace(b, anchor, "The mod falls back to its default table.</li>\n  </ul>\n" + root_section + "</section>")

# 3. Hardware table: host line.
b = must_replace(
    b,
    '<tr><td class="mod">CPU</td><td class="ver">800% (8 threads)</td><td>Adequate. Boot takes 25 seconds.</td></tr>',
    '<tr><td class="mod">CPU</td><td class="ver">800% (8 threads)</td><td>On an AMD Ryzen 7 9700X host (16 cores, Debian 12). Adequate; boot takes 25 seconds.</td></tr>',
)

# 4. Coverage: replace the "did not complete" paragraph with what actually happened.
start = b.index("<p><strong>Did not complete:</strong>")
end = b.index("</p>", start) + len("</p>")
coverage_new = (
    "<p><strong>Corrected after publication:</strong> the first version of this page reported that directory listings through the panel API had failed all session and attributed it to the node. That was wrong. The listings were being sent with paths rewritten by the local Git Bash shell "
    "(<code>/mods</code> arriving as <code>C:/Program Files/Git/mods</code>), and the panel answers a nonexistent path with the same <code>DaemonConnectionException</code> it would give for a real outage. With path conversion off, every listing works. "
    "<code>/kubejs</code> does not exist. The world's <code>datapacks/</code> folder is listed above. The server root, both world folders and the stray directories have been inventoried. The only remaining unattributed item is which jar ships the seven Botania recipes.</p>"
)
b = b[:start] + coverage_new + b[end:]

# 5. Review-count line.
b = must_replace(
    b,
    "<p><strong>Review passes on this document:</strong> one structural self-check of the page, one cross-check of every count and date against the extracted outputs. No independent review.</p>",
    "<p><strong>Review passes on this document:</strong> one structural self-check of the page, one cross-check of every count and date against the extracted outputs (which corrected three figures), and one correction pass after the root listing succeeded. No independent review.</p>",
)

body_path.write_text(b, encoding="utf-8")
full = (SP / "_shared_head.html").read_text(encoding="utf-8") + b
assert balanced(full), "audit not balanced"
(SP / "gscraft-server-audit.html").write_text(full, encoding="utf-8")
print("audit patched:", len(full), "chars, balanced")

# ------------------------------------------------------------------ blueprint
bp_path = SP / "wasteland-server-blueprint.html"
s = bp_path.read_text(encoding="utf-8")
s = must_replace(
    s,
    "<li><strong>File manager → delete</strong> <code>mods/</code>, <code>config/</code>, <code>defaultconfigs/</code>, the world folder, <code>kubejs/</code>, <code>crash-reports/</code>, <code>logs/</code>. Leave <code>libraries/</code>, the Forge jar and <code>eula.txt</code>. The wipe goes through the panel, not the API, while the node's file daemon is unstable.</li>",
    "<li><strong>File manager → delete</strong> <code>mods/</code>, <code>config/</code>, <code>defaultconfigs/</code>, both world folders (<code>Escape From Minenkrafte</code> and the remnant <code>Escape From Minecraft</code>), the stray root <code>region/</code>, <code>world/</code> and <code>serverconfig/</code>, <code>mods alternate/</code>, <code>tacz_backup/</code>, <code>crash-reports/</code>, <code>logs/</code>, the 531 MB <code>73160fed-…zip</code> and <code>hs_err_pid123.log</code>. Leave <code>libraries/</code>, the Forge jar and <code>eula.txt</code>. The wipe goes through the panel so a mistake is visible before it is committed.</li>",
)
assert balanced(s), "blueprint not balanced"
bp_path.write_text(s, encoding="utf-8")
print("blueprint patched:", len(s), "chars, balanced")
