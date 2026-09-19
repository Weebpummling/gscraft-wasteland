"""Can anything WALK into the walled compound except by the north gate? A flood fill over standable ground from a point on
the road north of the wall, read from the local world's region files. A step is one block up or up to three down; fences
and walls cannot be climbed; doors are counted as passable (the Dead break them on Hard) and reported. Each way in that is
found is plugged and the fill run again, until the yard cannot be reached."""
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, "G:/GSCraft/repo/tools")
from chests import Blocks  # noqa: E402

b = Blocks(Path("G:/GSCraft/server/wasteland-v8"))
X0, X1, Z0, Z1 = -950, -670, -970, -785          # the search area
BOX = (-900, -720, -920, -835)                    # the compound (x0, x1, z0, z1)
YARD = (-829, -893)
START = (-833, -940)                              # the road north of the gate
PASS = ("air", "cave_air", "grass", "tall_grass", "fern", "large_fern", "dead_bush", "snow", "torch", "wall_torch", "rail", "vine", "carpet", "button", "pressure_plate",
        "sign", "lever", "flower", "dandelion", "poppy", "sapling", "mushroom", "_door", "ladder", "cobweb", "sweet_berry_bush", "bush", "sugar_cane", "lantern", "chain")
NOCLIMB = ("_fence", "_wall", "fence_gate", "iron_bars", "glass_pane")


def kind(x, y, z):
    n = b.get(x, y, z).split(":", 1)[1]
    if any(n == k or n.endswith(k) for k in NOCLIMB):
        return "tall"
    if any(n == k or n.endswith(k) or (k.startswith("_") and k in n) for k in PASS):
        return "door" if "_door" in n else "open"
    if n in ("water", "lava"):
        return "open"
    return "solid"


cols = {}


def stands(x, z):
    if (x, z) not in cols:
        out = []
        ks = [kind(x, y, z) for y in range(52, 96)]
        for i in range(0, len(ks) - 2):
            if ks[i] == "solid" and ks[i + 1] in ("open", "door") and ks[i + 2] in ("open", "door"):
                out.append((52 + i + 1, ks[i + 1] == "door" or ks[i + 2] == "door"))
        cols[(x, z)] = out
    return cols[(x, z)]


def inside(x, z):
    return BOX[0] <= x <= BOX[1] and BOX[2] <= z <= BOX[3]


def fill(plugs):
    sy = min(stands(*START), key=lambda s: abs(s[0] - 70))[0]
    start = (START[0], sy, START[1])
    prev = {start: None}
    q = deque([start])
    while q:
        x, y, z = q.popleft()
        if (x, z) == YARD:
            path = []
            cur = (x, y, z)
            while cur:
                path.append(cur)
                cur = prev[cur]
            return path[::-1]
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, nz = x + dx, z + dz
            if not (X0 <= nx <= X1 and Z0 <= nz <= Z1) or any(abs(nx - px) <= 3 and abs(nz - pz) <= 3 for px, pz in plugs):
                continue
            for ny, _ in stands(nx, nz):
                if -3 <= ny - y <= 1 and (nx, ny, nz) not in prev:
                    prev[(nx, ny, nz)] = (x, y, z)
                    q.append((nx, ny, nz))
    return None


plugs = []
for n in range(12):
    path = fill(plugs)
    if path is None:
        print(f"with {len(plugs)} ways in plugged the yard cannot be reached on foot")
        break
    ci = next(i for i, p in enumerate(path) if inside(p[0], p[2]) and not inside(path[i - 1][0], path[i - 1][2]))

    def width(i):
        x, y, z = path[i]
        px, py, pz = path[i - 1]
        sx, sz = (0, 1) if px != x else (1, 0)      # across the direction of travel
        w = 1
        for sign in (1, -1):
            for k in range(1, 9):
                if any(abs(sy - y) <= 1 for sy, _ in stands(x + sign * sx * k, z + sign * sz * k)):
                    w += 1
                else:
                    break
        return w

    lo, hi = max(1, ci - 40), min(len(path) - 1, ci + 40)
    neck = min(range(lo, hi), key=lambda i: (width(i), abs(i - ci)))
    nx, ny, nz = path[neck]
    doors = [q for q in path[lo:hi] if any(d for y, d in stands(q[0], q[2]) if y == q[1])]
    print(f"way in {n + 1}: narrowest at ({nx}, {ny}, {nz}), {width(neck)} wide; enters the box at {path[ci]}; {len(path)} steps from the road" + (f"; a door at {doors[0]}" if doors else ""))
    plugs.append((nx, nz))
