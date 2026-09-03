"""Blueprint: rename-aside replaces the panel wipe; phase 02 executed; phase status lines."""
import pathlib
from html.parser import HTMLParser

SP = pathlib.Path(__file__).parent


def balanced(s):
    class P(HTMLParser):
        VOID = {"br", "img", "meta", "link", "hr", "input"}

        def __init__(self):
            super().__init__(); self.st, self.err = [], []

        def handle_starttag(self, t, a):
            if t not in self.VOID: self.st.append(t)

        def handle_endtag(self, t):
            if t in self.VOID: return
            if self.st and self.st[-1] == t: self.st.pop()
            else: self.err.append(t)
    q = P(); q.feed(s); return not q.err and not q.st


def rep(s, old, new):
    assert s.count(old) == 1, old[:80]
    return s.replace(old, new, 1)


pp = SP / "wasteland-server-blueprint.html"
s = pp.read_text(encoding="utf-8")

s = rep(s,
        "  <h3>Done by hand in the panel</h3>\n  <ul>\n",
        "  <h3>Nothing is deleted — old content is renamed aside</h3>\n  <ul>\n"
        "    <li><strong><code>/mods</code>, <code>/config</code> and <code>/defaultconfigs</code> were renamed to <code>…_old_20260902</code></strong> through the panel API, and the new world uses a new level name, so the old worlds are never touched and every step reverses with a rename. This replaces the panel-side wipe that an earlier version of this plan called for.</li>\n")

s = rep(s,
        "    <li><strong>File manager → delete</strong> <code>mods/</code>, <code>config/</code>, <code>defaultconfigs/</code>, both world folders (<code>Escape From Minenkrafte</code> and the remnant <code>Escape From Minecraft</code>), the stray root <code>region/</code>, <code>world/</code> and <code>serverconfig/</code>, <code>mods alternate/</code>, <code>tacz_backup/</code>, <code>crash-reports/</code>, <code>logs/</code>, the 531 MB <code>73160fed-…zip</code> and <code>hs_err_pid123.log</code>. Leave <code>libraries/</code>, the Forge jar and <code>eula.txt</code>. The wipe goes through the panel so a mistake is visible before it is committed.</li>",
        "    <li><strong>Housekeeping deferred to launch:</strong> the remnant worlds, the stray root <code>region/</code>, <code>world/</code>, <code>serverconfig/</code>, <code>mods alternate/</code>, <code>tacz_backup/</code>, the 531 MB zip and <code>hs_err_pid123.log</code> are deleted only after the new world is proven and the transplant verified — they are all in the local snapshot regardless.</li>")

s = rep(s,
        "<p>Wipe per the list above. Infrastructure only — ModernFix, FerriteCore, Canary, Spark, Chunky. <code>server.properties</code> corrected: view 10, simulation 6, whitelist on, a new level name and seed, <code>level-type=lostcities</code>. JVM flags confirmed.</p>",
        "<p><strong>Done 2026-09-02 15:12.</strong> Old content renamed aside; six jars — ModernFix, FerriteCore, Canary, Spark, Chunky, BHStats — into a fresh <code>/mods</code>; <code>server.properties</code> rewritten (throwaway world, view 10, simulation 6, whitelist on, watchdog restored); <code>AIKARS_ENABLED=1</code>; restart.</p>")
s = rep(s,
        "<div class=\"gate\"><b>Gate</b><br>Clean boot, zero ERROR lines, 20 TPS idle, baseline memory recorded.</div>",
        "<div class=\"gate\"><b>Gate · passed</b><br>Boot in 9.9 s, 0 ERROR lines, 25 benign warnings, 1.6 GB idle heap against 5.2 GB before.</div>")
assert balanced(s)
pp.write_text(s, encoding="utf-8")
print("blueprint patched")
