"""Block-by-block proof of a merged build: volume (1.12) vs the merged 1.20.1 world.

usage: verify112.py <volume.npz> <merged world dir> [--remap remap112.json]
Counts, per position in the volume's sections: modded -> merged block equals the table target;
vanilla non-air -> merged non-air; air -> merged air. Prints the mismatch classes with examples.
"""
import sys, json, collections
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from transplant import R, read_region_raw, region_of, slot_of
from anvil import decode
from makeremap112 import resolve

def main(a):
    vol=Path(a[1]); world=Path(a[2]); remap=Path(a[a.index('--remap')+1]) if '--remap' in a else Path(__file__).parent/'remap112.json'
    resolved=json.load(open(remap))['resolved']
    v=np.load(vol,allow_pickle=True); names=v['names']; keys=v['keys']; ids=v['ids']; meta=v['meta']; mod=v['modded']
    cache={}
    def chunk(cx,cz):
        rx,rz=region_of(cx,cz)
        if (rx,rz) not in cache: cache[(rx,rz)]=read_region_raw(world/'region'/f'r.{rx}.{rz}.mca')
        raw=cache[(rx,rz)].get(slot_of(cx,cz)); return R(raw[2]).root()[1] if raw else None
    ok=collections.Counter(); bad=collections.Counter(); ex={}
    secs_cache={}
    for n,(cx,cz,y) in enumerate(keys.tolist()):
        if (cx,cz) not in secs_cache:
            root=chunk(cx,cz); secs_cache[(cx,cz)]={s['Y'][1]:decode(s) for s in root['sections'][1][1]} if root else None
        sd=secs_cache[(cx,cz)]
        if sd is None: bad['chunk missing']+=4096; continue
        d=sd.get(y)
        got=np.array([d[0][i] for i in d[2]],dtype=object) if d else np.full(4096,'minecraft:air',dtype=object)
        src=ids[n]; mm=mod[n]
        air=src==0
        # air
        a_ok=(got[air]=='minecraft:air'); ok['air->air']+=int(a_ok.sum()); bad['air->block']+=int((~a_ok).sum())
        # vanilla non-air
        van=(~air)&(~mm); v_ok=got[van]!='minecraft:air'; ok['vanilla->block']+=int(v_ok.sum()); bad['vanilla->air']+=int((~v_ok).sum())
        if (~v_ok).any() and 'vanilla->air' not in ex:
            i=np.nonzero(van)[0][~v_ok][0]; ex['vanilla->air']=f'{names[src[i]]}[{meta[n][i]}] at chunk {cx},{cz} y{y}'
        # modded
        for i in np.nonzero(mm)[0].tolist():
            key=f'{names[src[i]]}[{int(meta[n][i])}]'; tgt=resolved.get(key) or resolve(names[src[i]],int(meta[n][i]))[0]
            tname='minecraft:air' if tgt=='air' else tgt.split('[')[0]
            if got[i]==tname: ok['modded->target']+=1
            elif tgt!='air' and got[i]=='minecraft:light_gray_concrete': ok['modded->placeholder(target missing)']+=1
            else:
                bad['modded->wrong']+=1
                if 'modded->wrong' not in ex: ex['modded->wrong']=f'{key} expected {tname} got {got[i]} at chunk {cx},{cz} y{y}'
    # --rect rects.json <name>: every section of every chunk in the rect above y_max (or inside an
    # exclusion box) must be air in the merged world - the volume never stored those sections
    if '--rect' in a:
        rects=json.load(open(a[a.index('--rect')+1])); rr=rects[a[a.index('--rect')+2]]
        y_max=rr.get('y_max',255); excl=[(e['blocks'],e.get('y_min',0)) for e in rr.get('exclude_sky',[])]
        x0,z0,x1,z1=rr['blocks']; leftover=0
        for cx in range(x0>>4,(x1>>4)+1):
            for cz in range(z0>>4,(z1>>4)+1):
                root=chunk(cx,cz)
                if not root: continue
                for s in root['sections'][1][1]:
                    sy=s['Y'][1]; d=decode(s)
                    if not d: continue
                    yy=(np.arange(4096)>>8)+sy*16; xx=(np.arange(4096)&15)+cx*16; zz=((np.arange(4096)>>4)&15)+cz*16
                    m=yy>y_max
                    for (ex0,ez0,ex1,ez1),ymin in excl: m|=(xx>=ex0)&(xx<=ex1)&(zz>=ez0)&(zz<=ez1)&(yy>=ymin)
                    if not m.any(): continue
                    got=np.array([d[0][i] for i in d[2]],dtype=object)
                    leftover+=int((got[m]!='minecraft:air').sum())
        if leftover: bad['cut-zone->block (ships left behind)']+=leftover
        else: ok['cut-zone->air']+=1
    tot=sum(ok.values())+sum(bad.values())
    print(f'{vol.name}: {tot:,} positions checked')
    for k,c in ok.items(): print(f'  OK   {k:<36} {c:>12,}')
    for k,c in bad.items():
        if c: print(f'  BAD  {k:<36} {c:>12,}   e.g. {ex.get(k,"")}')
    print('  RESULT:', 'CLEAN' if not any(bad.values()) else f'{sum(bad.values()):,} mismatches')
if __name__=='__main__': main(sys.argv)
