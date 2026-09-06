"""v8 road-network raster after the rework: surviving source roads + every road/bridge protect mask."""
import sys, json
from pathlib import Path
import numpy as np
from scipy import ndimage
sys.path.insert(0, r"G:/GSCraft/repo/tools")
from roadmask import RoadMask

CEN = Path(r"G:/GSCraft/incoming/census"); X0, Z0 = -3900, -3900
d = np.load(CEN / "v8_cell_pass7_inspect.npz", allow_pickle=True)
sn = d["sname"]; names = list(d["names"]); wt = d["wtop"].astype(np.int32)
H, W = sn.shape
cls = np.load(CEN / "classes.npy")
ROADMAT = {"minecraft:cobblestone","minecraft:stone","minecraft:andesite","minecraft:polished_andesite",
 "minecraft:polished_andesite_slab","minecraft:gravel","minecraft:light_gray_concrete","minecraft:stone_bricks",
 "minecraft:cracked_stone_bricks","minecraft:stone_slab","minecraft:smooth_stone_slab","minecraft:cobblestone_slab",
 "minecraft:mossy_cobblestone","minecraft:gray_concrete","minecraft:polished_blackstone","minecraft:stone_brick_slab",
 "minecraft:andesite_slab","minecraft:smooth_stone","minecraft:cobblestone_stairs","minecraft:stone_stairs",
 "minecraft:gray_concrete_powder","minecraft:brown_concrete_powder","minecraft:black_concrete","minecraft:coarse_dirt",
 "minecraft:andesite_wall","minecraft:white_concrete","minecraft:dirt_path"}
mat = np.isin(sn, np.array([i for i, n in enumerate(names) if n in ROADMAT], np.int32))
water = wt > -999
src = (cls == 1) & mat & ~water
rm = RoadMask(0)
new = rm.array()[:H, :W] & mat        # only where the carriageway is actually on the surface now
deck = rm.array()[:H, :W] & ~mat & ~water
net = src | new | deck
np.savez_compressed("roadnet.npz", net=net, src=src, new=new, deck=deck)
print(f"source {src.sum():,} + laid {new.sum():,} + decks {deck.sum():,} = {net.sum():,} px ({rm.n} masks)")
