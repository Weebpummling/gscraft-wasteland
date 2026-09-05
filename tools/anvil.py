"""Chunk section block access on top of transplant.py's typed NBT.
Sections: block_states = {palette: list of {Name, Properties}, data: long array (absent = all palette[0])}.
1.16+ packing: bits = max(4, ceil(log2(len(palette)))), entries never straddle longs.
"""
import math
from transplant import T_COMPOUND, T_STRING, T_LIST, T_LONGS, T_BYTE, T_INT

AIR = {"minecraft:air", "minecraft:cave_air", "minecraft:void_air"}


def _bits(n):
    return max(4, math.ceil(math.log2(n))) if n > 1 else 4


def decode(sec):
    """Return (palette names list, palette entries, indices list[4096]) or None if no block_states."""
    bs = sec.get("block_states")
    if not bs:
        return None
    pal = bs[1]["palette"][1][1]
    names = [p["Name"][1] for p in pal]
    data = bs[1].get("data")
    if not data:
        return names, pal, [0] * 4096
    bits = _bits(len(pal)); per = 64 // bits; mask = (1 << bits) - 1
    idx = [0] * 4096; i = 0
    for L in data[1]:
        L &= (1 << 64) - 1
        for k in range(per):
            if i >= 4096: break
            idx[i] = (L >> (k * bits)) & mask; i += 1
    return names, pal, idx


def encode(sec, pal, idx):
    """Write palette + indices back into the section (compacts unused palette entries)."""
    used = sorted(set(idx))
    remap = {old: new for new, old in enumerate(used)}
    pal2 = [pal[o] for o in used]
    idx2 = [remap[i] for i in idx]
    bs = sec["block_states"][1]
    bs["palette"] = (T_LIST, (T_COMPOUND, pal2))
    if len(pal2) == 1:
        bs.pop("data", None); return
    bits = _bits(len(pal2)); per = 64 // bits
    longs = []
    for start in range(0, 4096, per):
        L = 0
        for k, v in enumerate(idx2[start:start + per]):
            L |= v << (k * bits)
        if L >= 1 << 63: L -= 1 << 64
        longs.append(L)
    bs["data"] = (T_LONGS, longs)


def block_index(x, y, z):
    """x,y,z within section (0..15) -> index."""
    return (y << 8) | (z << 4) | x


class Chunk:
    """Wrap a parsed chunk root for get/set by world-relative-in-chunk coords (x 0..15, z 0..15, y absolute)."""

    def __init__(self, root):
        self.root = root
        self.secs = {}
        for sec in root.get("sections", (T_LIST, (T_COMPOUND, [])))[1][1]:
            y = sec["Y"][1]
            d = decode(sec)
            if d: self.secs[y] = [sec, d[0], d[1], d[2], False]

    def get(self, x, y, z):
        s = self.secs.get(y >> 4)
        if not s: return "minecraft:air"
        return s[1][s[3][block_index(x, y & 15, z)]]

    def set(self, x, y, z, name, props=None):
        s = self.secs.get(y >> 4)
        if not s:
            s = self._create_section(y >> 4)     # an empty section (no block_states) is created on demand
            if not s: return False
        sec, names, pal, idx, _ = s
        key = (name, tuple(sorted((props or {}).items())))
        for i, p in enumerate(pal):
            pp = p.get("Properties", (T_COMPOUND, {}))[1]
            if p["Name"][1] == name and tuple(sorted((k, v[1]) for k, v in pp.items())) == key[1]:
                pi = i; break
        else:
            entry = {"Name": (T_STRING, name)}
            if props: entry["Properties"] = (T_COMPOUND, {k: (T_STRING, v) for k, v in props.items()})
            pal.append(entry); names.append(name); pi = len(pal) - 1
        idx[block_index(x, y & 15, z)] = pi
        s[4] = True
        hm = self._heightmap()
        if hm is not None and name not in AIR and hm[(z << 4) | x] < y + 1:
            hm[(z << 4) | x] = y + 1          # keep the scan hint valid after raising ground
        return True

    def _create_section(self, sy):
        """Give a missing or empty section (within -4..19) block_states so blocks can be placed in it."""
        if sy < -4 or sy > 19: return None
        lst = self.root.setdefault("sections", (T_LIST, (T_COMPOUND, [])))[1][1]
        sec = next((s for s in lst if s["Y"][1] == sy), None)
        if sec is None:
            sec = {"Y": (T_BYTE, sy), "biomes": (T_COMPOUND, {"palette": (T_LIST, (T_STRING, ["minecraft:plains"]))})}
            lst.append(sec); lst.sort(key=lambda s: s["Y"][1])
        air = {"Name": (T_STRING, "minecraft:air")}
        sec["block_states"] = (T_COMPOUND, {"palette": (T_LIST, (T_COMPOUND, [air]))})
        self.secs[sy] = [sec, ["minecraft:air"], [air], [0] * 4096, False]
        return self.secs[sy]

    def _heightmap(self):
        """MOTION_BLOCKING heightmap decoded to 256 heights (top non-air y + 1), or None."""
        if hasattr(self, "_hm"): return self._hm
        self._hm = None
        hm = self.root.get("Heightmaps")
        if hm and "MOTION_BLOCKING" in hm[1]:
            longs = hm[1]["MOTION_BLOCKING"][1]; bits = 9; per = 64 // bits; out = []
            for L in longs:
                L &= (1 << 64) - 1
                for k in range(per):
                    if len(out) >= 256: break
                    out.append(((L >> (k * bits)) & 0x1FF) - 64)
            if len(out) == 256: self._hm = out
        return self._hm

    def surface_hint(self, x, z):
        """A y from which scanning downward is safe (heightmap top, or the world top)."""
        hm = self._heightmap()
        if hm is None: return 319
        return min(319, hm[(z << 4) | x] + 2)

    def top(self, x, z, ymin=-64, ymax=None, ignore=AIR):
        if ymax is None: ymax = self.surface_hint(x, z)
        for y in range(ymax, ymin - 1, -1):
            n = self.get(x, y, z)
            if n not in ignore: return y, n
        return ymin - 1, "minecraft:air"

    def dirty(self):
        return any(s[4] for s in self.secs.values())

    def commit(self):
        """Write changed sections back; drop heightmaps and light so the game recomputes them."""
        for y, (sec, names, pal, idx, d) in self.secs.items():
            if d: encode(sec, pal, idx)
        if self.dirty():
            self.root.pop("Heightmaps", None)
            self.root["isLightOn"] = (T_BYTE, 0)
            for sec in self.root.get("sections", (T_LIST, (T_COMPOUND, [])))[1][1]:
                sec.pop("BlockLight", None); sec.pop("SkyLight", None)
