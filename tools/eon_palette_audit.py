# Eon palette audit: CVD distinguishability + non-text contrast on light/dark backgrounds.
# Palette basis: Okabe & Ito (2008) colorblind-safe set, reordered to alternate warm/cool
# so adjacent eons (and consecutive at-a-glance rows) stay distinct.
import colorsys, math

EON_ORDER=["Hadean","Archean","Proterozoic","Paleozoic","Mesozoic","Cenozoic"]
LIGHT={"Hadean":"#D55E00","Archean":"#56B4E9","Proterozoic":"#E69F00",
       "Paleozoic":"#009E73","Mesozoic":"#CC79A7","Cenozoic":"#0072B2"}
WHITE_BG="#ffffff"; DARK_BG="#262626"   # representative Blowfish dark body bg

def h2rgb(h): h=h.lstrip("#"); return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
def lin(c): return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
def L(hexc):
    r,g,b=map(lin,h2rgb(hexc)); return 0.2126*r+0.7152*g+0.0722*b
def contrast(a,b):
    la,lb=L(a),L(b); hi,lo=max(la,lb),min(la,lb); return (hi+0.05)/(lo+0.05)
def text_on(hexc):  # pick black/white by higher contrast (WCAG)
    return ("#111111",contrast(hexc,"#111111")) if contrast(hexc,"#111111")>=contrast(hexc,"#ffffff") else ("#ffffff",contrast(hexc,"#ffffff"))

# --- CIE Lab + dE76 ---
def xyz(hexc):
    r,g,b=map(lin,h2rgb(hexc))
    return (r*0.4124+g*0.3576+b*0.1805, r*0.2126+g*0.7152+b*0.0722, r*0.0193+g*0.1192+b*0.9505)
def lab(hexc):
    X,Y,Z=xyz(hexc); Xn,Yn,Zn=0.95047,1.0,1.08883
    def f(t): return t**(1/3) if t>0.008856 else 7.787*t+16/116
    fx,fy,fz=f(X/Xn),f(Y/Yn),f(Z/Zn)
    return (116*fy-16,500*(fx-fy),200*(fy-fz))
def de76(a,b):
    la,lb=lab(a),lab(b); return math.sqrt(sum((x-y)**2 for x,y in zip(la,lb)))

# --- CVD simulation (Machado et al. 2009, severity 1.0) applied in linear RGB ---
M={"protan":[[0.152286,1.052583,-0.204868],[0.114503,0.786281,0.099216],[-0.003882,-0.048116,1.051998]],
   "deutan":[[0.367322,0.860646,-0.227968],[0.280085,0.672501,0.047413],[-0.011820,0.042940,0.968881]],
   "tritan":[[1.255528,-0.076749,-0.178779],[-0.078411,0.930809,0.147602],[0.004733,0.691367,0.303900]]}
def delin(x): x=max(0,min(1,x)); return 12.92*x if x<=0.0031308 else 1.055*x**(1/2.4)-0.055
def sim(hexc,kind):
    if kind=="normal": return hexc
    r,g,b=map(lin,h2rgb(hexc)); m=M[kind]
    o=[m[i][0]*r+m[i][1]*g+m[i][2]*b for i in range(3)]
    return "#"+"".join("%02X"%round(delin(v)*255) for v in o)

def adj_min(pal,kind):
    vals=[de76(sim(pal[EON_ORDER[i]],kind),sim(pal[EON_ORDER[i+1]],kind)) for i in range(5)]
    return min(vals),vals

# --- derive dark-theme palette: lighten (HSL) only colors too dim on dark bg ---
def lighten(hexc,step=0.04):
    r,g,b=h2rgb(hexc); h,l,s=colorsys.rgb_to_hls(r,g,b)
    l=min(0.95,l+step); r,g,b=colorsys.hls_to_rgb(h,l,s)
    return "#"+"".join("%02X"%round(c*255) for c in (r,g,b))
DARK=dict(LIGHT); MIN_NONTEXT=3.0
for k in EON_ORDER:
    while contrast(DARK[k],DARK_BG)<MIN_NONTEXT: DARK[k]=lighten(DARK[k])

print("=== NON-TEXT CONTRAST (WCAG 1.4.11 graphical objects, target >=3.0) ===")
print(f"{'Eon':12} {'light':8} cWhite cDark   {'dark':8} cDark")
for k in EON_ORDER:
    print(f"{k:12} {LIGHT[k]:8} {contrast(LIGHT[k],WHITE_BG):5.2f} {contrast(LIGHT[k],DARK_BG):5.2f}   {DARK[k]:8} {contrast(DARK[k],DARK_BG):5.2f}")

print("\n=== BAR LABEL TEXT (3 wide bands shown; pick black/white) ===")
for k in ["Hadean","Archean","Proterozoic"]:
    t,c=text_on(LIGHT[k]); print(f"{k:12} fill {LIGHT[k]} -> text {t} (contrast {c:.2f})")

print("\n=== ADJACENT-EON SEPARATION  dE76 (>10 clearly distinct) ===")
for label,pal in [("LIGHT",LIGHT),("DARK",DARK)]:
    print(f" [{label}]")
    for kind in ["normal","protan","deutan","tritan"]:
        mn,vals=adj_min(pal,kind)
        print(f"   {kind:7} min={mn:5.1f}  pairs="+", ".join(f"{v:.0f}" for v in vals))

print("\n=== DARK OVERRIDES NEEDED (differ from light) ===")
print({k:DARK[k] for k in EON_ORDER if DARK[k]!=LIGHT[k]} or "none")
