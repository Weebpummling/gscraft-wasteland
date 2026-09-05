"""Census of a world folder: built-chunk map, palette, top-down render. usage: census_world.py <world dir> <label> <px_per_block>"""
import sys, struct, zlib, gzip, collections, json, hashlib
sys.path.insert(0, r'G:\GSCraft\repo\tools')
from pathlib import Path
from transplant import R
from anvil import decode
from PIL import Image, ImageDraw
W=Path(sys.argv[1]); LABEL=sys.argv[2]; PPB=float(sys.argv[3]); OUT=Path(r'G:\GSCraft\incoming\census')
NAT=set('minecraft:'+n for n in 'air cave_air void_air stone dirt grass_block water sand gravel bedrock deepslate andesite diorite granite tuff coal_ore iron_ore copper_ore oak_leaves oak_log birch_leaves birch_log spruce_leaves spruce_log grass short_grass tall_grass fern large_fern snow podzol coarse_dirt clay lava sandstone dark_oak_leaves dark_oak_log moss_block dripstone_block calcite smooth_basalt snow_block mud dead_bush'.split())
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
    lvl=root.get('Level'); 
    if lvl: root=lvl[1]                     # 1.16 layout
    secs=root.get('sections') or root.get('Sections')
    return secs[1][1] if secs else []
def decode_any(s):
    if 'block_states' in s: return decode(s)
    pal=s.get('Palette'); 
    if not pal: return None
    names=[p['Name'][1] for p in pal[1][1]]
    st=s.get('BlockStates')
    if not st: return names, None, [0]*4096
    bits=max(4,(len(names)-1).bit_length()); idx=[0]*4096; i=0
    longs=[(v & (1<<64)-1) for v in st[1]]
    # 1.16+ packed without spanning
    per=64//bits; mask=(1<<bits)-1
    for L in longs:
        for k in range(per):
            if i>=4096: break
            idx[i]=(L>>(k*bits))&mask; i+=1
    return names,None,idx
built={}; pal=collections.Counter(); tops={}; ymin_all=999
files=sorted((W/'region').glob('r.*.mca'))
for f in files:
    rx,rz=map(int,f.stem.split('.')[1:3])
    for slot,raw in regs(f).items():
        cx,cz=rx*32+(slot&31),rz*32+(slot>>5)
        try: root=R(raw).root()[1]
        except Exception: continue
        b=0; top={}
        for s in sorted(sections_of(root), key=lambda s:s['Y'][1]):
            dd=decode_any(s)
            if not dd: continue
            names,_,idx=dd; sy=s['Y'][1]*16
            cnt=collections.Counter(idx)
            for i,c in cnt.items():
                n=names[i]; pal[n]+=c
                if n not in NAT: b+=c
            if PPB>0:
                air={i for i,n in enumerate(names) if n in ('minecraft:air','minecraft:cave_air','minecraft:void_air')}
                if len(air)==len(names): continue
                for i,v in enumerate(idx):
                    if v in air: continue
                    top[(i&15,(i>>4)&15)]=(sy+(i>>8),names[v])
        built[(cx,cz)]=b
        if top: tops[(cx,cz)]=top
xs=[c[0] for c in built]; zs=[c[1] for c in built]
X0,Z0,X1,Z1=min(xs)*16,min(zs)*16,max(xs)*16+15,max(zs)*16+15
print(f'{LABEL}: chunks {len(built)} | blocks x {X0}..{X1} z {Z0}..{Z1} | built>=200: {sum(1 for v in built.values() if v>=200)} | built>=2000: {sum(1 for v in built.values() if v>=2000)}')
print(' namespaces:', collections.Counter(n.split(':')[0] for n in pal).most_common(5))
json.dump({'bbox':[X0,Z0,X1,Z1],'built':{f'{k[0]},{k[1]}':v for k,v in built.items()},'palette':pal.most_common()}, open(OUT/f'{LABEL}_census.json','w'))
# built map (ascii, 1 char per chunk) to file
with open(OUT/f'{LABEL}_builtmap.txt','w') as fh:
    for cz in range(min(zs),max(zs)+1):
        fh.write(''.join(('#' if built.get((cx,cz),0)>=2000 else '+' if built.get((cx,cz),0)>=200 else '.' if (cx,cz) in built else ' ') for cx in range(min(xs),max(xs)+1))+'\n')
# render
COL={'grass_block':(90,140,60),'dirt':(110,80,50),'stone':(120,120,120),'water':(40,80,180),'sand':(210,200,150),'bricks':(150,70,60),'stone_bricks':(110,110,110),'polished_andesite':(140,140,140),'smooth_stone':(160,160,160),'oak_planks':(170,130,80),'cobblestone':(105,105,105),'white_concrete':(230,230,230),'light_gray_concrete':(150,150,150),'gray_concrete':(80,80,80),'yellow_concrete':(220,190,40),'iron_block':(200,200,210),'oak_leaves':(50,110,40),'spruce_leaves':(40,90,50),'birch_leaves':(70,130,50),'vine':(60,120,50),'glass':(180,220,240),'farmland':(120,90,50),'dirt_path':(150,120,80),'snow':(240,240,250),'gravel':(130,125,120),'coarse_dirt':(100,75,50),'moss_block':(80,130,60),'black_concrete':(20,20,20),'terracotta':(150,90,60),'grass':(95,150,65),'tall_grass':(95,150,65),'podzol':(90,70,40),'sandstone':(215,205,160),'smooth_sandstone':(215,205,160),'white_terracotta':(200,180,160),'light_gray_terracotta':(140,120,110),'andesite':(130,130,130),'cyan_terracotta':(80,100,100),'birch_log':(200,190,160),'spruce_log':(80,60,40),'oak_log':(110,85,50),'concrete_powder':(180,180,180)}
def col(n):
    k=n.split(':')[1]
    if k in COL: return COL[k]
    h=hashlib.md5(k.encode()).digest(); return (70+h[0]//2,70+h[1]//2,70+h[2]//2)
if PPB>0:
    w=int((X1-X0+1)*PPB); h=int((Z1-Z0+1)*PPB); im=Image.new('RGB',(w,h),(0,0,0)); px=im.load()
    for (cx,cz),top in tops.items():
        for (lx,lz),(y,n) in top.items():
            X=int((cx*16+lx-X0)*PPB); Z=int((cz*16+lz-Z0)*PPB)
            if 0<=X<w and 0<=Z<h:
                r,g,b=col(n); f2=0.55+0.45*min(1,max(0,(y-40)/90)); px[X,Z]=(int(r*f2),int(g*f2),int(b*f2))
    d=ImageDraw.Draw(im); d.rectangle([0,0,w,18],fill=(0,0,0)); d.text((6,4),f'{LABEL} top-down, {PPB} px/block, x {X0}..{X1} z {Z0}..{Z1}',fill=(255,255,255))
    im.save(OUT/f'{LABEL}_topdown.png'); print(' render', OUT/f'{LABEL}_topdown.png', im.size)
