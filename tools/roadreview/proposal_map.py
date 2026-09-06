import json, sys; sys.path.insert(0,".")
from pathlib import Path
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw
CEN = Path(r"G:/GSCraft/incoming/census"); PLAN = Path(r"G:/GSCraft/repo/buildmap/plan_v8"); X0, Z0 = -3900, -3900
d = np.load(CEN / "v8_cell_pass7_inspect.npz", allow_pickle=True)
gy = d["gy"].astype(np.float32); wt = d["wtop"].astype(np.int32); built_m = d["built"]
water = wt > -999; H, W = gy.shape
z = np.load("roadnet.npz"); net = z["net"]; new = z["new"] | z["deck"]
g = ndimage.gaussian_filter(np.where(gy > -999, gy, 60), 2); dzz, dxx = np.gradient(g)
sh = np.clip(0.66 + 0.34*(dxx*0.7 - dzz*0.7)/3.0, 0.3, 1.0)
img = np.zeros((H, W, 3), np.float32)
img[:] = np.array([203, 206, 193]) * sh[..., None] / 255.0
img[water] = np.array([0.32, 0.46, 0.64]); img[built_m & ~water] = np.array([0.46, 0.44, 0.43])
img[net] = np.array([70, 66, 62])/255.0                      # inherited + all roads: dark
img[new] = np.array([210, 150, 40])/255.0                    # the v8 connectors: amber
S = 3
im = Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).resize((W//S, H//S), Image.LANCZOS)
dr = ImageDraw.Draw(im)
links = json.load(open("mstlinks.json"))
def px(p): return ((p[0]-X0)//S, (p[1]-Z0)//S)
for L in links:
    dd, a, b, pa, pb = L["d"], L["a"], L["b"], L["pa"], L["pb"]
    col = (235,30,30) if dd >= 60 else ((250,140,0) if dd >= 20 else (255,225,0))
    x0,y0 = px(pa); x1,y1 = px(pb)
    dr.line([x0,y0,x1,y1], fill=col, width=3)
    r = 9 if dd >= 60 else 6
    dr.ellipse([x0-r,y0-r,x0+r,y0+r], outline=col, width=2)
    dr.ellipse([x1-r,y1-r,x1+r,y1+r], outline=col, width=2)
    if dd >= 20: dr.text((x0+r+2, y0-6), f"{dd:.0f} m", fill=col)
for p in json.load(open(PLAN/"sectors_v8.json"))["sectors"]:
    if p.get("group")=="removed": continue
    x0,z0,x1,z1 = (p["x0"]-X0)//S,(p["z0"]-Z0)//S,(p["x1"]-X0)//S,(p["z1"]-Z0)//S
    dr.rectangle([x0,z0,x1,z1], outline=(255,255,255)); dr.text((x0, z0-11), p["id"], fill=(255,255,255))
leg = [((70,66,62),"road inherited from the source maps"),((210,150,40),"v8 connectors, viaducts and bridges (16.4 km)"),
       ((235,30,30),"break needing new road (>=60 m)"),((250,140,0),"break needing a patch (20-60 m)"),((255,225,0),"hairline break (<20 m)")]
dr.rectangle([6,6,430,6+len(leg)*15+6], fill=(245,245,240))
for k,(c,t) in enumerate(leg):
    dr.rectangle([12,12+k*15,26,22+k*15], fill=c); dr.text((32,12+k*15), t, fill=(20,20,20))
im.save("v8_road_proposal.png"); print("wrote v8_road_proposal.png", im.size)
