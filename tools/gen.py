import json, math, re, itertools as _it
T=json.load(open('teams.json')); AL=json.load(open('all_alignments.json'))
US=json.load(open('us-states.json')); CA=json.load(open('canada.json'))
LAT1,LAT2,LAT0,LON0=29.5,45.5,37.5,-96.0
r1,r2,r0c,l0=map(math.radians,(LAT1,LAT2,LAT0,LON0))
nn=(math.sin(r1)+math.sin(r2))/2; Cc=math.cos(r1)**2+2*nn*math.sin(r1); rho0=math.sqrt(Cc-2*nn*math.sin(r0c))/nn
def alb(lon,lat):
    lam,phi=math.radians(lon),math.radians(lat); rho=math.sqrt(Cc-2*nn*math.sin(phi))/nn; th=nn*(lam-l0)
    return rho*math.sin(th), rho0-rho*math.cos(th)
def feat_rings(geojson, keep=None):
    out=[]
    for f in geojson['features']:
        nm=f['properties'].get('name','')
        if keep and nm not in keep: continue
        g=f['geometry']; polys=g['coordinates'] if g['type']=='Polygon' else [r for p in g['coordinates'] for r in p]
        if g['type']=='Polygon': polys=g['coordinates']
        elif g['type']=='MultiPolygon': polys=[r for p in g['coordinates'] for r in p]
        else: polys=[]
        for ring in polys: out.append([(x,y) for x,y in ring])
    return out
US_RINGS=feat_rings(US, keep=None)
US_RINGS=[r for r in US_RINGS if not any(False for _ in r)]  # all
# drop AK/HI by name
US_RINGS=[]
for f in US['features']:
    if f['properties']['name'] in {'Alaska','Hawaii','Puerto Rico'}: continue
    g=f['geometry']; polys=g['coordinates'] if g['type']=='Polygon' else [r for p in g['coordinates'] for r in p]
    for ring in polys: US_RINGS.append([(x,y) for x,y in ring])
CA_KEEP={'British Columbia','Alberta','Manitoba','Ontario','Quebec','Saskatchewan'}
CA_RINGS=[]
for f in CA['features']:
    if f['properties'].get('name') not in CA_KEEP: continue
    g=f['geometry']; polys=g['coordinates'] if g['type']=='Polygon' else [r for p in g['coordinates'] for r in p]
    for ring in polys: CA_RINGS.append([(x,y) for x,y in ring if y<=58])

DIVCOL=["#5aa9e6","#E8743B","#2CA76F","#E36FA8","#E6A52C","#7FC7EE","#A07CE0","#B7B13A"]
ANCHORS=[("Pacific Northwest",47,-122),("Pacific",35,-119),("Mountain",40,-110),("Southwest",33,-112),
("South Central",31,-96),("North Central",45,-94),("Great Lakes",42,-85),("Mid-South",36,-87),
("Southeast",31,-83),("Florida",27,-81),("Mid-Atlantic",39,-77),("Northeast",42,-72),
("Western Canada",51,-114),("Eastern Canada",46,-74),("Texas",31,-98),("Plains",39,-96)]
def autoname(cents):
    used=set(); names=[]
    for la,lo in cents:
        for a in sorted(ANCHORS,key=lambda a:(a[1]-la)**2+0.6*(a[2]-lo)**2):
            if a[0] not in used: used.add(a[0]); names.append(a[0]); break
    return names
# Curated geographic names for NFL full-optimization (C) divisions; other leagues' C divisions auto-name.
NFL_C={("49ers","Chargers","Raiders","Rams"):"Pacific",("Broncos","Cardinals","Seahawks","Vikings"):"Mountain",
("Chiefs","Cowboys","Saints","Texans"):"South Central",("Bears","Browns","Lions","Packers"):"Great Lakes",
("Eagles","Giants","Jets","Patriots"):"Northeast",("Bills","Commanders","Ravens","Steelers"):"Mid-Atlantic",
("Bengals","Colts","Panthers","Titans"):"Mid-South",("Buccaneers","Dolphins","Falcons","Jaguars"):"Southeast"}

def _cent(lg,ts):
    return (sum(T[lg][t]["lat"] for t in ts)/len(ts), sum(T[lg][t]["lon"] for t in ts)/len(ts))

def real_divs_of_conf(lg,confname):
    """(realname,(lat,lon)) for each real division of confname, taken from the actual (A) alignment."""
    for c,divs in AL[lg]["A"]:
        if c==confname: return [(dn,_cent(lg,ts)) for dn,ts in divs]
    return []

def assign_real_names(lg,confname,bdivs):
    """Map this conference's real division names onto the optimized B divisions by best geographic fit."""
    real=real_divs_of_conf(lg,confname)
    if len(real)!=len(bdivs): return [None]*len(bdivs)   # counts differ -> fall through to auto-name
    bc=[_cent(lg,ts) for _,ts in bdivs]; best=None; bp=None
    for perm in _it.permutations(range(len(real))):
        cost=sum((bc[i][0]-real[perm[i]][1][0])**2+(bc[i][1]-real[perm[i]][1][1])**2 for i in range(len(bc)))
        if best is None or cost<best: best=cost; bp=perm
    return [real[bp[i]][0] for i in range(len(bc))]

def named_struct(lg,struct,kind):
    """A: keep real names. B: reuse real division names (geographic best-fit). C: curated/auto geographic,
    but keep already-meaningful names such as MLS West/East."""
    out=[]
    for conf,divs in struct:
        if kind=="B":
            nm=assign_real_names(lg,conf,divs)
            nd=[(nm[i],divs[i][1]) for i in range(len(divs))]
        else:
            nd=[]
            for dn,ts in divs:
                if kind=="A": name=dn
                elif kind=="C":
                    if lg=="nfl": name=NFL_C.get(tuple(sorted(ts)),None)
                    elif re.match(r"^d\d+$",dn): name=None      # generic placeholder -> auto geographic
                    else: name=dn                               # already meaningful (e.g. MLS West/East)
                else: name=None
                nd.append((name,ts))
        out.append((conf,nd))
    # auto-name any remaining None (generic C divisions, or B where counts didn't match)
    flat=[(ci,di,ts) for ci,(c,dv) in enumerate(out) for di,(nm,ts) in enumerate(dv) if nm is None]
    if flat:
        cents=[_cent(lg,ts) for _,_,ts in flat]; nms=autoname(cents)
        for (ci,di,ts),nm in zip(flat,nms):
            c,dv=out[ci]; dv[di]=(nm,dv[di][1])
    return out

def _canon_order(lg):
    """Logical west->east order of real division names per conference, taken from the actual (A) alignment.
    Shared by the A and B panels so identical division names occupy identical legend slots (hence colors)."""
    order={}
    for conf,divs in AL[lg]["A"]:
        order[conf]=[dn for dn,ts in sorted(divs,key=lambda d:_cent(lg,d[1])[1])]
    return order

def _reorder(lg,out,kind):
    """A and B: lock divisions to the one canonical name order (matching colors across both panels).
    C: one uniform geographic sort for every league: western conference first, then divisions
    strictly west->east by longitude with a north->south latitude tiebreak."""
    if kind=="C":
        out=[(conf,sorted(divs,key=lambda nd:(_cent(lg,nd[1])[1],-_cent(lg,nd[1])[0]))) for conf,divs in out]
        out=sorted(out,key=lambda cd:sum(_cent(lg,ts)[1] for _,ts in cd[1])/len(cd[1]))
        return out
    canon=_canon_order(lg)
    res=[]
    for conf,divs in out:
        seq=canon.get(conf)
        if seq:
            pos={nm:i for i,nm in enumerate(seq)}
            divs=sorted(divs,key=lambda nd:pos.get(nd[0],99))
        res.append((conf,divs))
    return res

def build_panel_struct(lg,kind):
    return _reorder(lg, named_struct(lg, AL[lg][kind], kind), kind)

def project_fit(lg, structs):
    teams=T[lg]; pts=[alb(v["lon"],v["lat"]) for v in teams.values()]
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    dx=max(xs)-min(xs); dy=max(ys)-min(ys); mx=0.10*dx; my=0.10*dy
    minx,maxx,miny,maxy=min(xs)-mx,max(xs)+mx,min(ys)-my,max(ys)+my
    W,H,PAD=900,560,4
    s=min((W-2*PAD)/(maxx-minx),(H-2*PAD)/(maxy-miny))
    ox=PAD+((W-2*PAD)-(maxx-minx)*s)/2; oy=PAD+((H-2*PAD)-(maxy-miny)*s)/2
    def S(p): return (ox+(p[0]-minx)*s, oy+(maxy-p[1])*s)
    return S,W,H

def wedge(cx,cy,ri,ro,a0,a1,col,extra=""):
    lg=1 if (a1-a0)>math.pi else 0
    x0o,y0o=cx+ro*math.cos(a0),cy+ro*math.sin(a0); x1o,y1o=cx+ro*math.cos(a1),cy+ro*math.sin(a1)
    x1i,y1i=cx+ri*math.cos(a1),cy+ri*math.sin(a1); x0i,y0i=cx+ri*math.cos(a0),cy+ri*math.sin(a0)
    return (f'<path {extra} d="M{x0o:.1f},{y0o:.1f} A{ro},{ro} 0 {lg} 1 {x1o:.1f},{y1o:.1f} L{x1i:.1f},{y1i:.1f} '
            f'A{ri},{ri} 0 {lg} 0 {x0i:.1f},{y0i:.1f} Z" fill="{col}" stroke="var(--map-bg)" stroke-width="0.5" vector-effect="non-scaling-stroke"/>')

def content(lg, struct, S, rings, focus=None):
    teams=T[lg]
    flat=[(nm,ts,conf) for conf,divs in struct for nm,ts in divs]
    tdiv={t:i for i,(_,ts,_) in enumerate(flat) for t in ts}
    f=None if focus is None else int(focus)
    true_xy={t:S(alb(teams[t]["lon"],teams[t]["lat"])) for t in teams}
    THRESH=1.0; VENUE=2.0; tl=list(teams); used=set(); ren={}; clusters=[]
    for t in tl:
        if t in used: continue
        cl=[u for u in tl if u not in used and math.hypot(true_xy[u][0]-true_xy[t][0],true_xy[u][1]-true_xy[t][1])<THRESH]
        used.update(cl)
        if len(cl)==1: ren[t]=true_xy[t]
        else:
            cx=sum(true_xy[u][0] for u in cl)/len(cl); cy=sum(true_xy[u][1] for u in cl)/len(cl); R=8+2*(len(cl)-1)
            # Preserve geography: place each team in the compass direction of its true
            # position relative to the cluster center, so north stays up and east stays
            # right. Teams that truly share a venue sit on the center and have no
            # meaningful direction, so they fan out evenly among themselves instead.
            coloc=[u for u in cl if math.hypot(true_xy[u][0]-cx,true_xy[u][1]-cy)<VENUE]
            for u in cl:
                if u in coloc: continue
                a=math.atan2(true_xy[u][1]-cy,true_xy[u][0]-cx); ren[u]=(cx+R*math.cos(a),cy+R*math.sin(a))
            for k,u in enumerate(sorted(coloc)):
                a=-math.pi/2+2*math.pi*k/max(len(coloc),1); ren[u]=(cx+R*math.cos(a),cy+R*math.sin(a))
            clusters.append((cx,cy,sorted(cl),len(coloc)==len(cl)))
    DR=5.4
    def lbl_place(t):
        # initial guess: place the label away from nearby teams
        x,y=ren[t]
        near=[u for u in teams if u!=t and math.hypot(ren[u][0]-x,ren[u][1]-y)<36]
        if near:
            ax=sum(ren[u][0] for u in near)/len(near); ay=sum(ren[u][1] for u in near)/len(near)
            ux,uy=x-ax,y-ay; n=math.hypot(ux,uy) or 1; ux,uy=ux/n,uy/n
        else:
            ux,uy=0.0,-1.0
        o=DR+3
        if abs(uy)>=abs(ux):
            return [x, y-o, "middle"] if uy<0 else [x, y+o+6.5, "middle"]
        return [x+o+1, y+2.5, "start"] if ux>0 else [x-o-1, y+2.5, "end"]
    lpos={t:lbl_place(t) for t in teams}
    def lbox(t):
        lx,ly,anch=lpos[t]; w=len(teams[t]["abbr"])*4.3
        x0,x1=(lx-w/2,lx+w/2) if anch=="middle" else (lx-w,lx) if anch=="end" else (lx,lx+w)
        return x0,x1,ly-6.5,ly+1.5
    # nudge any overlapping labels apart vertically until none collide (handles
    # same-venue-adjacent pairs like Yankees/Mets that land on one point)
    for _ in range(40):
        moved=False
        for a,b in _it.combinations(list(teams),2):
            A=lbox(a); B=lbox(b)
            if A[1]<=B[0] or B[1]<=A[0] or A[3]<=B[2] or B[3]<=A[2]: continue
            shift=(min(A[3],B[3])-max(A[2],B[2]))/2+0.6
            if lpos[a][1]<=lpos[b][1]: lpos[a][1]-=shift; lpos[b][1]+=shift
            else: lpos[a][1]+=shift; lpos[b][1]-=shift
            moved=True
        if not moved: break
    out=[]
    for r in rings:
        pr=[S(alb(x,y)) for x,y in r]
        d="M"+" L".join(f"{x:.1f},{y:.1f}" for x,y in pr)+"Z"
        out.append(f'<path d="{d}" fill="none" stroke="currentColor" stroke-width="0.7" vector-effect="non-scaling-stroke" opacity="0.20"/>')
    for i,(name,tms,conf) in enumerate(flat):
        col=f"var(--div{i%len(DIVCOL)})"; active=(f is not None and i==f); dim=(f is not None and i!=f)
        sw=2.6 if active else 1.3; dr=6.7 if active else 5.4
        gstyle=' style="opacity:0.1"' if dim else ''; gcls='div active' if active else 'div'
        cx=sum(true_xy[t][0] for t in tms)/len(tms); cy=sum(true_xy[t][1] for t in tms)/len(tms)
        g=[f'<g class="{gcls}" data-i="{i}" data-name="{name}"{gstyle}>']
        for t in tms:
            tx,ty=true_xy[t]; g.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" stroke="{col}" stroke-width="{sw}" vector-effect="non-scaling-stroke" stroke-opacity="0.6"/>')
        for t in tms:
            x,y=ren[t]; tx,ty=true_xy[t]
            if abs(x-tx)>0.5 or abs(y-ty)>0.5:
                g.append(f'<line class="fan" x1="{tx:.1f}" y1="{ty:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="currentColor" stroke-width="1.0" vector-effect="non-scaling-stroke" stroke-opacity="0.5"/>')
        for t in tms:
            d=teams[t]; x,y=ren[t]; tx,ty=true_xy[t]
            cls="team fan" if (abs(x-tx)>0.5 or abs(y-ty)>0.5) else "team"
            glow=' style="filter:drop-shadow(0 0 3px currentColor)"' if active else ''
            lx,ly,anch=lpos[t]
            g.append(f'<g class="{cls}"><circle cx="{x:.1f}" cy="{y:.1f}" r="{dr}" fill="{d["fill"]}" stroke="{d["ring"]}" stroke-width="2" vector-effect="non-scaling-stroke"{glow}><title>{t} ({name})</title></circle>'
                     f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="7" text-anchor="{anch}" fill="currentColor" stroke="var(--map-bg)" stroke-width="2.5" paint-order="stroke" stroke-linejoin="round" opacity="0.95" style="font-family:ui-monospace,monospace">{d["abbr"]}</text></g>')
        g.append('</g>'); out.append("".join(g))
    out.append('<g class="donuts">')
    for cx,cy,cl,venue in clusters:
        k=len(cl); tip=("Shared venue: " if venue else "Nearby teams: ")+", ".join(cl); ids=sorted(set(str(tdiv[t]) for t in cl))
        ddim=(f is not None and str(f) not in ids); dstyle=' style="opacity:0.1"' if ddim else ''
        out.append(f'<g class="donut" data-is="{",".join(ids)}"{dstyle}><title>{tip}</title>')
        for j,t in enumerate(sorted(cl)):
            a0=-math.pi/2+2*math.pi*j/k; a1=-math.pi/2+2*math.pi*(j+1)/k
            wdim=(f is not None and not ddim and tdiv[t]!=f); ws=' style="opacity:0.12"' if wdim else ''
            out.append(wedge(cx,cy,3.4,7.0,a0,a1,teams[t]["fill"],extra=f'class="wedge" data-i="{tdiv[t]}"{ws}'))
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.2" fill="var(--map-bg)" stroke="currentColor" stroke-width="0.6" vector-effect="non-scaling-stroke" opacity="0.85"/>')
        out.append(f'<text x="{cx:.1f}" y="{cy+2.2:.1f}" font-size="6" text-anchor="middle" fill="currentColor" style="font-family:ui-monospace,monospace">{k}</text></g>')
    out.append('</g>')
    return "\n".join(out)

PANELTITLE={"A":"Current Divisions","B":"Conferences Kept, Divisions Optimized","C":"Full Geographic Optimization"}
def legend(struct,pid):
    blocks=[]; gi=0
    for conf,divs in struct:
        btns=[]
        for nm,ts in divs:
            sw=f'<span style="display:inline-block;width:11px;height:11px;border-radius:50%;background:var(--div{gi%len(DIVCOL)});margin-right:5px;vertical-align:middle"></span>'
            btns.append(f'<button class="leg" data-for="{pid}" data-i="{gi}" style="padding:2px 7px;border-radius:6px;font-size:12.5px;border:none;background:none;color:inherit;cursor:pointer">{sw}{nm}</button>'); gi+=1
        blocks.append(f'<div style="display:flex;align-items:center;gap:2px;flex-wrap:wrap;margin:2px 0"><span style="font-weight:700;font-size:12px;opacity:.75;min-width:36px">{conf}</span>{"".join(btns)}</div>')
    return f'<div style="margin:8px 0">{"".join(blocks)}<button class="leg" data-for="{pid}" data-i="all" style="padding:2px 7px;border-radius:6px;font-size:12px;opacity:.65;border:none;background:none;color:inherit;cursor:pointer">Show All</button></div>'

JS=r"""<style>
svg[data-z="0"] .fan{opacity:0}
svg[data-z="1"] .donuts{opacity:0;pointer-events:none}
.donut{cursor:pointer}.div,.donut,.wedge,.div line,.div circle{transition:opacity .12s,stroke-width .12s}
.div.active line{stroke-width:2.6;stroke-opacity:1}.div.active circle{r:6.7;filter:drop-shadow(0 0 3px currentColor)}
.div.active text{font-weight:700;opacity:1}.leg.active{background:rgba(255,255,255,.16)!important;font-weight:700;outline:1px solid rgba(255,255,255,.25)}
</style><script>
function wire(id){
 const svg=document.getElementById(id),vp=svg.querySelector('.vp');let scale=1,tx=0,ty=0,drag=0,p0,t0,moved=0,locked=null;const Z=2.4,W=900,H=560;
 const ap=()=>{vp.setAttribute('transform',`translate(${tx} ${ty}) scale(${scale})`);svg.setAttribute('data-z',scale>=Z?'1':'0');};
 const toS=e=>{const p=svg.createSVGPoint();p.x=e.clientX;p.y=e.clientY;return p.matrixTransform(svg.getScreenCTM().inverse());};
 svg.addEventListener('wheel',e=>{e.preventDefault();const p=toS(e),f=e.deltaY<0?1.12:1/1.12,ns=Math.min(9,Math.max(1,scale*f));tx=p.x-(p.x-tx)*(ns/scale);ty=p.y-(p.y-ty)*(ns/scale);scale=ns;ap();},{passive:0});
 svg.addEventListener('pointerdown',e=>{drag=1;moved=0;svg.style.cursor='grabbing';svg.setPointerCapture(e.pointerId);p0=toS(e);t0=[tx,ty];});
 svg.addEventListener('pointermove',e=>{if(!drag)return;moved=1;const p=toS(e);tx=t0[0]+(p.x-p0.x);ty=t0[1]+(p.y-p0.y);ap();});
 svg.addEventListener('pointerup',()=>{drag=0;svg.style.cursor='grab';});
 svg.addEventListener('dblclick',()=>{scale=1;tx=0;ty=0;ap();});
 const divs=[...svg.querySelectorAll('.div')],dn=[...svg.querySelectorAll('.donut')],lg=[...document.querySelectorAll(`.leg[data-for="${id}"]`)];
 dn.forEach(d=>d.addEventListener('click',e=>{e.stopPropagation();const b=d.getBBox(),cx=b.x+b.width/2,cy=b.y+b.height/2;scale=3.4;tx=W/2-cx*scale;ty=H/2-cy*scale;ap();}));
 function setF(i){const s=(i==null)?null:String(i);
  divs.forEach(d=>{const on=(s==null||d.dataset.i===s);d.style.opacity=on?'1':'0.1';d.classList.toggle('active',s!=null&&on);});
  dn.forEach(d=>{const ids=d.dataset.is.split(',');if(s==null){d.style.opacity='1';d.querySelectorAll('.wedge').forEach(w=>w.style.opacity='1');}
   else if(ids.includes(s)){d.style.opacity='1';d.querySelectorAll('.wedge').forEach(w=>w.style.opacity=(w.dataset.i===s)?'1':'0.12');}else d.style.opacity='0.1';});
  lg.forEach(b=>b.classList.toggle('active',s!=null&&b.dataset.i===s));}
 divs.forEach(d=>{d.addEventListener('mouseenter',()=>{if(locked==null)setF(d.dataset.i);});d.addEventListener('mouseleave',()=>{if(locked==null)setF(null);});
  d.addEventListener('click',e=>{if(moved)return;locked=(locked===d.dataset.i)?null:d.dataset.i;setF(locked);e.stopPropagation();});});
 svg.addEventListener('click',()=>{if(!moved){locked=null;setF(null);}});
 lg.forEach(b=>{b.addEventListener('mouseenter',()=>{if(locked==null)setF(b.dataset.i==='all'?null:b.dataset.i);});b.addEventListener('mouseleave',()=>{if(locked==null)setF(null);});
  b.addEventListener('click',()=>{if(b.dataset.i==='all'){locked=null;setF(null);}else{locked=(locked===b.dataset.i)?null:b.dataset.i;setF(locked);}});});
 ap();}
document.querySelectorAll('svg.realign').forEach(s=>wire(s.id));
</script>"""

LEAGUE_NAME={"nfl":"NFL","mlb":"MLB","nba":"NBA","nhl":"NHL","mls":"MLS"}
PANELS={"nfl":["A","B","C"],"mlb":["A","B","C"],"nba":["A","B","C"],"nhl":["A","B","C"],"mls":["A","C"]}
INSTR=("Scroll to zoom, drag to pan, double-click to reset. Click a division in the key to lock focus. "
       "Teams sharing a venue show as one split marker; zoom in or click it to fan them out. Every other team sits at its true location.")

# Theme block: each map follows the embedding page's light/dark mode (Blowfish toggles .dark on
# <html>), falling back to the OS preference when viewed standalone. Background and text come from
# CSS variables so one SVG renders in both themes; geography and labels already use currentColor.
DARKVARS=("--map-bg:#14191F;--map-fg:#E6EDF3;--map-border:#30363d;"
          "--div0:#5aa9e6;--div1:#E8743B;--div2:#2CA76F;--div3:#E36FA8;"
          "--div4:#E6A52C;--div5:#7FC7EE;--div6:#A07CE0;--div7:#B7B13A")
LIGHTVARS=("--map-bg:#ffffff;--map-fg:#1f2328;--map-border:#d0d7de;"
           "--div0:#1f6fb2;--div1:#c2521a;--div2:#1f7d52;--div3:#c43d80;"
           "--div4:#a9760f;--div5:#0e7490;--div6:#6f4bc2;--div7:#7e7a1f")
THEME=('<style>'
 ':root{' + DARKVARS + '}'
 ':root.mapdark{' + DARKVARS + '}'
 ':root.maplight{' + LIGHTVARS + '}'
 '@media (prefers-color-scheme: light){:root{' + LIGHTVARS + '}}'
 '</style>'
 '<script>(function(){var R=document.documentElement;'
 'function t(){var d;try{d=(window.parent&&window.parent!==window)'
 '?window.parent.document.documentElement.classList.contains("dark"):null;}catch(e){d=null;}'
 'if(d===null)d=matchMedia("(prefers-color-scheme: dark)").matches;'
 'R.classList.toggle("mapdark",d);R.classList.toggle("maplight",!d);}t();'
 'try{if(window.parent&&window.parent!==window)new MutationObserver(t)'
 '.observe(window.parent.document.documentElement,{attributes:true,attributeFilter:["class"]});}catch(e){}'
 'try{matchMedia("(prefers-color-scheme: dark)").addEventListener("change",t);}catch(e){}})();</script>')

def panel_doc(lg,k,st,S,W,H,rings):
    """One standalone, single-panel, theme-aware interactive HTML file."""
    pid=f"{lg}_{k}"
    title=PANELTITLE[k]
    if lg=="mlb" and k in "AB": title+=" (AL / NL)"
    if lg=="nba":
        if k=="A": title="Projected Divisions"
        title+=" (with Seattle and Las Vegas)"
    svg=(f'<svg id="{pid}" class="realign" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
         f'data-z="0" style="width:100%;height:auto;touch-action:none;cursor:grab;color:var(--map-fg);'
         f'background:var(--map-bg);border-radius:8px;border:1px solid var(--map-border)"><g class="vp">{content(lg,st,S,rings)}</g></svg>')
    return ('<!doctype html><meta charset=utf-8>'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{LEAGUE_NAME[lg]} {title}</title>'
            '<body style="margin:0;background:var(--map-bg);color:var(--map-fg);font-family:system-ui;'
            'padding:14px;max-width:940px;margin:auto">'
            + THEME +
            f'<p style="opacity:.7;font-size:12px;margin:0 0 8px">{INSTR}</p>'
            f'<h3 style="margin:20px 0 0">{title}</h3>{legend(st,pid)}{svg}{JS}</body>')

for lg in ["nfl","mlb","nba","nhl","mls"]:
    structs={k:build_panel_struct(lg,k) for k in PANELS[lg]}
    rings=US_RINGS+(CA_RINGS if lg in("nhl","mls") else [])
    S,W,H=project_fit(lg,structs)
    for k in PANELS[lg]:
        open(f'fig_{lg}_{k}.html','w').write(panel_doc(lg,k,structs[k],S,W,H,rings))
        open(f'thumb_{lg}_{k}.svg','w').write(
            f'<svg viewBox="0 0 900 560" xmlns="http://www.w3.org/2000/svg" data-z="0" '
            f'style="color:#E6EDF3"><style>:root{{--map-bg:#14191F}}.fan{{opacity:0}}</style>'
            f'{content(lg,structs[k],S,rings)}</svg>')
    print("built",lg,"panels",PANELS[lg])
print("done: one theme-aware file per panel -> fig_<league>_<panel>.html")
