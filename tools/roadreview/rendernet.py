import json
from pathlib import Path
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw
CEN = Path(r"G:/GSCraft/incoming/census"); PLAN = Path(r"G:/GSCraft/repo/buildmap/plan_v8"); X0, Z0 = -3900, -3900
d = np.load(CEN / "v8_cell_pass10_inspect.npz", allow_pickle=True)
gy = d["gy"].astype(np.float32); wt = d["wtop"].astype(np.int32); built = d["built"]
water = wt > -999; H, W = gy.shape
corr = np.load("corr.npy"); z = np.load("roadnet.npz"); net = z["net"]
sizes = {int(v): int((corr==v).sum()) for v in np.unique(corr) if v}
ids = sorted(sizes, key=lambda k: -sizes[k])
rank = {cid: k for k, cid in enumerate(ids)}
# base: hillshade
g = ndimage.gaussian_filter(np.where(gy > -999, gy, 60), 2)
dzz, dxx = np.gradient(g)
sh = np.clip(0.62 + 0.38*(dxx*0.7 - dzz*0.7)/3.0, 0.25, 1.0)
img = np.zeros((H, W, 3), np.float32)
img[:] = np.array([196, 199, 186]) * sh[..., None] / 255.0
img[water] = np.array([0.30, 0.44, 0.62])
img[built & ~water] = np.array([0.42, 0.40, 0.40])
PAL = [(228,52,52),(40,110,235),(245,170,30),(30,175,110),(180,70,215),(0,190,200),(255,120,180),(140,110,60)]
for cid in ids:
    m = corr == cid
    c = PAL[rank[cid]] if rank[cid] < len(PAL) else (90,90,90)
    img[m] = np.array(c)/255.0
other = net & (corr == 0)
img[other] = np.array([120,120,120])/255.0
im = Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8))
S = 3
im = im.resize((W//S, H//S), Image.LANCZOS)
dr = ImageDraw.Draw(im)
for p in json.load(open(PLAN/"sectors_v8.json"))["sectors"]:
    if p.get("group")=="removed": continue
    x0,z0,x1,z1 = (p["x0"]-X0)//S,(p["z0"]-Z0)//S,(p["x1"]-X0)//S,(p["z1"]-Z0)//S
    dr.rectangle([x0,z0,x1,z1], outline=(255,255,255))
    dr.text((x0, z0-11), p["id"], fill=(255,255,255))
for k, cid in enumerate(ids[:8]):
    dr.rectangle([8, 8+k*14, 20, 18+k*14], fill=PAL[k])
    dr.text((26, 8+k*14), f"C{k+1}  {sizes[cid]:,} px", fill=(20,20,20))
im.save("v8_roadnet.png")
print("wrote v8_roadnet.png", im.size)
