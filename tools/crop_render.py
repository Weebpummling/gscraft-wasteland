"""usage: crop_render.py <world> <label> <x0> <z0> <x1> <z1> <px_per_block>  - top-down crop + surface height stats"""
import sys, struct, zlib, gzip, collections, hashlib
sys.path.insert(0, r'G:\GSCraft\repo\tools')
from pathlib import Path
from transplant import R
from anvil import decode
from PIL import Image, ImageDraw
exec(open(r'G:\GSCraft\incoming\census\census_world.py').read().split('built={}')[0].split('W=Path')[0])  # imports only
W=Path(sys.argv[1]); LABEL=sys.argv[2]; X0,Z0,X1,Z1=map(int,sys.argv[3:7]); PPB=float(sys.argv[7])
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
def sections_of(root):
    lvl=root.get('Level')
    if lvl: root=lvl[1]
    secs=root.get('sections') or root.get('Sections'); return secs[1][1] if secs else []
def decode_any(s):
    if 'block_states' in s: return decode(s)
    pal=s.get('Palette')
    if not pal: return None
    names=[p['Name'][1] for p in pal[1][1]]; st=s.get('BlockStates')
    if not st: return names,None,[0]*4096
    bits=max(4,(len(names)-1).bit_length()); idx=[0]*4096; i=0; per=64//bits; mask=(1<<bits)-1
    for L in st[1]:
        L&=(1<<64)-1
        for k in range(per):
            if i>=4096: break
            idx[i]=(L>>(k*bits))&mask; i+=1
    return names,None,idx
COL={'grass_block':(90,140,60),'dirt':(110,80,50),'stone':(120,120,120),'water':(40,80,180),'sand':(210,200,150),'bricks':(150,70,60),'stone_bricks':(110,110,110),'polished_andesite':(140,140,140),'smooth_stone':(160,160,160),'oak_planks':(170,130,80),'cobblestone':(105,105,105),'white_concrete':(230,230,230),'light_gray_concrete':(150,150,150),'gray_concrete':(80,80,80),'yellow_concrete':(220,190,40),'iron_block':(200,200,210),'oak_leaves':(50,110,40),'spruce_leaves':(40,90,50),'birch_leaves':(70,130,50),'vine':(60,120,50),'glass':(180,220,240),'farmland':(120,90,50),'dirt_path':(150,120,80),'gravel':(130,125,120),'coarse_dirt':(100,75,50),'moss_block':(80,130,60),'black_concrete':(20,20,20),'terracotta':(150,90,60),'grass':(95,150,65),'tall_grass':(95,150,65),'podzol':(90,70,40),'andesite':(130,130,130),'cobblestone_slab':(105,105,105),'stone_brick_slab':(110,110,110),'tuff_bricks':(120,125,115),'polished_tuff':(135,140,130),'white_terracotta':(200,180,160),'light_gray_terracotta':(140,120,110),'cyan_terracotta':(80,100,100),'stone_slab':(125,125,125),'smooth_stone_slab':(160,160,160),'polished_deepslate':(70,70,75),'deepslate_tiles':(60,60,65),'azalea_leaves':(70,120,50),'dark_oak_wood':(60,45,30),'birch_log':(200,190,160),'spruce_log':(80,60,40),'oak_log':(110,85,50)}
def col(n):
    k=n.split(':')[1]
    if k in COL: return COL[k]
    h=hashlib.md5(k.encode()).digest(); return (70+h[0]//2,70+h[1]//2,70+h[2]//2)
RCACHE={}
w=int((X1-X0+1)*PPB); h=int((Z1-Z0+1)*PPB); im=Image.new('RGB',(w,h),(0,0,0)); px=im.load(); ys=collections.Counter(); ground=collections.Counter()
for cx in range(X0>>4,(X1>>4)+1):
    for cz in range(Z0>>4,(Z1>>4)+1):
        key=(cx>>5,cz>>5)
        if key not in RCACHE:
            f=W/'region'/f'r.{key[0]}.{key[1]}.mca'; RCACHE[key]=regs(f) if f.exists() else {}
        raw=RCACHE[key].get((cz&31)*32+(cx&31))
        if not raw: continue
        try: root=R(raw).root()[1]
        except Exception: continue
        top={}
        for s in sorted(sections_of(root), key=lambda s:s['Y'][1]):
            dd=decode_any(s)
            if not dd: continue
            names,_,idx=dd; sy=s['Y'][1]*16
            air={i for i,n in enumerate(names) if n in ('minecraft:air','minecraft:cave_air','minecraft:void_air')}
            if len(air)==len(names): continue
            for i,v in enumerate(idx):
                if v in air: continue
                top[(i&15,(i>>4)&15)]=(sy+(i>>8),names[v])
        for (lx,lz),(y,n) in top.items():
            x,z=cx*16+lx,cz*16+lz
            if X0<=x<=X1 and Z0<=z<=Z1:
                ys[y]+=1
                if n in ('minecraft:grass_block','minecraft:dirt','minecraft:grass','minecraft:tall_grass','minecraft:coarse_dirt','minecraft:podzol'): ground[y]+=1
                r,g,b=col(n); f2=0.55+0.45*min(1,max(0,(y-40)/90)); px[min(w-1,int((x-X0)*PPB)),min(h-1,int((z-Z0)*PPB))]=(int(r*f2),int(g*f2),int(b*f2))
d=ImageDraw.Draw(im); d.rectangle([0,0,w,18],fill=(0,0,0)); d.text((6,4),f'{LABEL}  x {X0}..{X1} z {Z0}..{Z1}  {PPB} px/block',fill=(255,255,255))
out=rf'G:\GSCraft\incoming\census\{LABEL}.png'; im.save(out)
tot=sum(ys.values()); srt=sorted(ys.items())
def pct(p):
    acc=0
    for y,c in srt:
        acc+=c
        if acc>=tot*p: return y
print(f'{LABEL}: {out} {im.size} | surface y p5 {pct(.05)} median {pct(.5)} p95 {pct(.95)} | natural ground y: {sorted(ground.items(), key=lambda kv:-kv[1])[:5]}')
