"""Per-block surface class raster for the Pripyat cell -> classes.npy (uint8) + preview PNG.
0 ground, 1 road, 2 rail, 3 water, 4 building (surface above y 68, not leaves), 5 tree/leaves, 6 sand/dirt path, 7 missing"""
import sys, struct, zlib, gzip, collections
sys.path.insert(0, r'G:\GSCraft\repo\tools')
from pathlib import Path
import numpy as np
from transplant import R
from anvil import decode
from PIL import Image
W=Path(r'G:\GSCraft\scratch\upgrade\pripyat_after\world'); X0,Z0,X1,Z1=-3900,-3900,1200,700
ROAD={'cobblestone','stone','andesite','polished_andesite','polished_andesite_slab','gravel','light_gray_concrete','stone_bricks','cracked_stone_bricks','stone_slab','smooth_stone_slab','cobblestone_slab','mossy_cobblestone','gray_concrete','polished_blackstone','stone_brick_slab','andesite_slab','smooth_stone','cobblestone_stairs','stone_stairs','gray_concrete_powder','brown_concrete_powder','black_concrete'}
RAIL={'rail','powered_rail','detector_rail','activator_rail'}
NATURAL={'grass_block','dirt','grass','tall_grass','fern','large_fern','coarse_dirt','podzol','sand','dirt_path','snow','mycelium','moss_block','dandelion','poppy','azure_bluet','oxeye_daisy','cornflower','dead_bush','sweet_berry_bush','mud','rooted_dirt','clay','red_sand','gravel_path'}
def regs(f):
    data=f.read_bytes(); out={}
    for slot in range(1024):
        off=struct.unpack_from('>I',data,slot*4)[0]; start=(off>>8)*4096
        if start==0 or start+5>len(data): continue
        length=struct.unpack_from('>I',data,start)[0]; comp=data[start+4]
        if start+4+length>len(data): continue
        raw=data[start+5:start+4+length]
        try: out[slot]=zlib.decompress(raw) if comp==2 else gzip.decompress(raw)
        except Exception: pass
    return out
H=Z1-Z0+1; Wd=X1-X0+1
cls=np.full((H,Wd),7,np.uint8); hgt=np.zeros((H,Wd),np.int16); gnd=np.zeros((H,Wd),np.int16)
GROUND={'grass_block','dirt','coarse_dirt','podzol','sand','gravel','stone','mycelium','mud','rooted_dirt','clay','red_sand','snow_block','moss_block','andesite','granite','diorite','sandstone','red_sandstone','terracotta','water','farmland','dirt_path','grass_path'}
for rx in range(X0>>9,(X1>>9)+1):
    for rz in range(Z0>>9,(Z1>>9)+1):
        f=W/'region'/f'r.{rx}.{rz}.mca'
        if not f.exists(): continue
        for slot,raw in regs(f).items():
            cx,cz=rx*32+(slot&31),rz*32+(slot>>5)
            if cx*16>X1 or cx*16+15<X0 or cz*16>Z1 or cz*16+15<Z0: continue
            try: root=R(raw).root()[1]
            except Exception: continue
            secs=root.get('sections')
            if not secs: continue
            top={}; rail={}; ground={}
            for s in sorted(secs[1][1], key=lambda s:s['Y'][1]):
                if s['Y'][1]>7: break
                dd=decode(s)
                if not dd: continue
                names,_,idx=dd; sy=s['Y'][1]*16
                air={i for i,n in enumerate(names) if n in ('minecraft:air','minecraft:cave_air')}
                if len(air)==len(names): continue
                short=[n.split(':')[1] for n in names]
                for i,v in enumerate(idx):
                    if v in air: continue
                    k=(i&15,(i>>4)&15); yb=sy+(i>>8); top[k]=(yb,short[v])
                    if short[v] in RAIL: rail[k]=1
                    if short[v] in GROUND and yb<=90: ground[k]=yb
            for (lx,lz),(y,n) in top.items():
                x,z=cx*16+lx,cz*16+lz
                if not (X0<=x<=X1 and Z0<=z<=Z1): continue
                c=0
                if (lx,lz) in rail: c=2
                elif n in ('water','lily_pad','seagrass','kelp','ice'): c=3
                elif n in ROAD and y<=72: c=1
                elif n in NATURAL: c=6 if n in ('sand','coarse_dirt','dirt_path','dirt') else 0
                elif 'leaves' in n or n in ('vine','azalea','flowering_azalea'): c=5
                else: c=4
                cls[z-Z0,x-X0]=c; hgt[z-Z0,x-X0]=y; gnd[z-Z0,x-X0]=ground.get((lx,lz),y)
np.save('classes.npy',cls); np.save('surface_y.npy',hgt); np.save('ground_y.npy',gnd)
PAL=[(70,110,50),(200,200,200),(230,140,40),(40,80,190),(120,80,80),(30,60,30),(170,150,110),(0,0,0)]
im=Image.fromarray(cls,'P'); im.putpalette(sum(PAL,())); im.convert('RGB').resize((Wd//3,H//3),Image.NEAREST).save('classes_small.png')
print('classes:', {i:int((cls==i).sum()) for i in range(8)})
