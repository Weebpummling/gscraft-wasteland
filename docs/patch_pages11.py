"""Endgame loop per the user's design: timed set-up per location, one randomly drawn target per
cycle with warning, retake on loss, radio-tower repair loot everywhere, countdown, wave defence at
the main base, boss in the final wave."""
import pathlib, re
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


def sub1(s, pattern, repl):
    n = len(re.findall(pattern, s, flags=re.S))
    assert n == 1, (pattern[:60], n)
    return re.sub(pattern, lambda m: repl, s, count=1, flags=re.S)


p = SP / "wasteland-server-blueprint.html"
s = p.read_text(encoding="utf-8")

s = sub1(s, r"<p>The fix is to move the cost from reaching to <strong>holding</strong>\..*?</p>",
         "<p>The old premise had the Tarkov problem: once the players have max gear, every location is the same loop. So the cost moves from gear to <strong>time</strong>. Territory you can lose is the only scarcity the engine reliably provides, and with five players the loss has to be threatened one place at a time.</p>")
s = sub1(s, r"<p>Each held strongpoint also becomes a named target:.*?</p>",
         "<p><strong>Taking a location starts a clock.</strong> The players get a set amount of time to build defences, structures and gear at that location before it is attacked on a set cycle. If they are defeated, or die, the position is lost and must be retaken from the garrison. If they win, the position is held, and holding it buys more time to explore and clear the next points of interest. <strong>Every cleared POI joins the pool</strong> from which the game draws, at random, the one that will be attacked next, with a warning ahead of time like a 7 Days to Die blood moon: the radio tower broadcast and the quest book name the site and the night. One site per attack; five players cannot hold five compounds and are never asked to. Every location also yields the loot that repairs the radio tower.</p>")
s = sub1(s, r"<h3>The Signal[^<]*</h3>\s*<p>.*?</p>",
         "<h3>The Signal: a finale that comes to you</h3>\n  <p>Repairing the radio tower needs the loot every held location drops. <strong>Completing it starts a countdown to the big one.</strong> When the timer runs out the finale is a wave defence at the players' main base, the hideout they have been living in, never at a strongpoint: escalating waves against the base, and the final wave carries the boss. The base is whichever claim the group marks as home in the quest book. The fight happens on ground the players built, with everything they own on the table.</p>")
s = sub1(s, r'<div><div class="step">Loop . 02</div><h4>Take</h4><p>.*?</p></div>',
         '<div><div class="step">Loop &middot; 02</div><h4>Take</h4><p>Clear a garrisoned location. The clock starts: a set time to fortify it before the first attack. Each held location unlocks a tech tier and adds itself to the target pool.</p></div>')
s = sub1(s, r'<div><div class="step">Loop . 03</div><h4>Hold</h4><p>.*?</p></div>',
         '<div><div class="step">Loop &middot; 03</div><h4>Defend</h4><p>On the cycle the game draws one held location and warns the players. Win and it stays held, with more time to explore; lose or die and it must be retaken.</p></div>')
s = sub1(s, r'<div><div class="step">Loop . 04</div><h4>Signal</h4><p>.*?</p></div>',
         '<div><div class="step">Loop &middot; 04</div><h4>Signal</h4><p>Tower repaired from the loot the locations drop, the countdown runs, and the waves come to the main base. The last wave brings the boss. Then the season increments and it starts harder.</p></div>')
s = sub1(s, r"<p>Implementation is FTB Quests for the visible progression.*?</p>",
         "<p>Implementation is FTB Quests for the visible progression and the home-claim marker, In Control! for garrison composition, KubeJS for the location state machine, the clock, the target draw, the countdown and the wave director, and The Hordes for the attack nights. All four are already in the stack for other reasons.</p>")
assert balanced(s)
p.write_text(s, encoding="utf-8")
print("blueprint endgame patched")

m = SP / "wasteland-district-map.html"
t = m.read_text(encoding="utf-8")
old = "Sized as compounds to hold on a horde night, not as single buildings:"
assert t.count(old) == 1
t = t.replace(old, "Sized as compounds to fortify and defend on the night the game draws them, not as single buildings:")
m.write_text(t, encoding="utf-8")
print("map wording patched")
