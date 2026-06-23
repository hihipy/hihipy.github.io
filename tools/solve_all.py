import math, itertools, json, pulp
from collections import defaultdict, Counter
R=3958.8
def hav(a,b):
    la1,lo1,la2,lo2=map(math.radians,[a[0],a[1],b[0],b[1]]); dla,dlo=la2-la1,lo2-lo1
    h=math.sin(dla/2)**2+math.cos(la1)*math.cos(la2)*math.sin(dlo/2)**2; return 2*R*math.asin(math.sqrt(h))
def T(n,la,lo,c,d): return {"name":n,"lat":la,"lon":lo,"conf":c,"div":d}
LEAGUES={
"nfl":[T("Bills",42.774,-78.787,"AFC","East"),T("Dolphins",25.958,-80.239,"AFC","East"),T("Patriots",42.091,-71.264,"AFC","East"),T("Jets",40.814,-74.074,"AFC","East"),
T("Ravens",39.278,-76.623,"AFC","North"),T("Bengals",39.095,-84.516,"AFC","North"),T("Browns",41.506,-81.700,"AFC","North"),T("Steelers",40.447,-80.016,"AFC","North"),
T("Texans",29.685,-95.411,"AFC","South"),T("Colts",39.760,-86.164,"AFC","South"),T("Jaguars",30.324,-81.637,"AFC","South"),T("Titans",36.166,-86.771,"AFC","South"),
T("Broncos",39.744,-105.020,"AFC","West"),T("Chiefs",39.049,-94.484,"AFC","West"),T("Raiders",36.091,-115.184,"AFC","West"),T("Chargers",33.953,-118.339,"AFC","West"),
T("Cowboys",32.748,-97.093,"NFC","East"),T("Giants",40.814,-74.074,"NFC","East"),T("Eagles",39.901,-75.168,"NFC","East"),T("Commanders",38.908,-76.864,"NFC","East"),
T("Bears",41.862,-87.617,"NFC","North"),T("Lions",42.340,-83.046,"NFC","North"),T("Packers",44.501,-88.062,"NFC","North"),T("Vikings",44.974,-93.258,"NFC","North"),
T("Falcons",33.755,-84.401,"NFC","South"),T("Panthers",35.226,-80.853,"NFC","South"),T("Saints",29.951,-90.081,"NFC","South"),T("Buccaneers",27.976,-82.503,"NFC","South"),
T("Cardinals",33.528,-112.263,"NFC","West"),T("Rams",33.953,-118.339,"NFC","West"),T("49ers",37.403,-121.970,"NFC","West"),T("Seahawks",47.595,-122.332,"NFC","West")],
"nhl":[T("Bruins",42.366,-71.062,"East","Atlantic"),T("Sabres",42.875,-78.876,"East","Atlantic"),T("Red Wings",42.341,-83.055,"East","Atlantic"),T("Panthers",26.158,-80.326,"East","Atlantic"),
T("Canadiens",45.496,-73.569,"East","Atlantic"),T("Senators",45.297,-75.927,"East","Atlantic"),T("Lightning",27.943,-82.452,"East","Atlantic"),T("Maple Leafs",43.643,-79.379,"East","Atlantic"),
T("Hurricanes",35.803,-78.722,"East","Metropolitan"),T("Blue Jackets",39.969,-83.006,"East","Metropolitan"),T("Devils",40.734,-74.171,"East","Metropolitan"),T("Islanders",40.711,-73.723,"East","Metropolitan"),
T("Rangers",40.750,-73.993,"East","Metropolitan"),T("Flyers",39.901,-75.172,"East","Metropolitan"),T("Penguins",40.439,-79.989,"East","Metropolitan"),T("Capitals",38.898,-77.021,"East","Metropolitan"),
T("Blackhawks",41.881,-87.674,"West","Central"),T("Avalanche",39.749,-105.008,"West","Central"),T("Stars",32.790,-96.810,"West","Central"),T("Wild",44.945,-93.101,"West","Central"),
T("Predators",36.159,-86.778,"West","Central"),T("Blues",38.627,-90.203,"West","Central"),T("Mammoth",40.768,-111.901,"West","Central"),T("Jets",49.893,-97.144,"West","Central"),
T("Ducks",33.808,-117.877,"West","Pacific"),T("Flames",51.038,-114.052,"West","Pacific"),T("Oilers",53.547,-113.498,"West","Pacific"),T("Kings",34.043,-118.267,"West","Pacific"),
T("Sharks",37.333,-121.901,"West","Pacific"),T("Kraken",47.622,-122.354,"West","Pacific"),T("Canucks",49.278,-123.109,"West","Pacific"),T("Golden Knights",36.103,-115.178,"West","Pacific")],
"mlb":[T("Orioles",39.284,-76.622,"AL","East"),T("Red Sox",42.346,-71.097,"AL","East"),T("Yankees",40.829,-73.926,"AL","East"),T("Rays",27.768,-82.653,"AL","East"),T("Blue Jays",43.641,-79.389,"AL","East"),
T("White Sox",41.830,-87.634,"AL","Central"),T("Guardians",41.496,-81.685,"AL","Central"),T("Tigers",42.339,-83.049,"AL","Central"),T("Royals",39.051,-94.481,"AL","Central"),T("Twins",44.982,-93.278,"AL","Central"),
T("Astros",29.757,-95.355,"AL","West"),T("Angels",33.800,-117.883,"AL","West"),T("Athletics",36.0994,-115.17,"AL","West"),T("Mariners",47.591,-122.332,"AL","West"),T("Rangers",32.747,-97.082,"AL","West"),
T("Braves",33.890,-84.468,"NL","East"),T("Marlins",25.778,-80.220,"NL","East"),T("Mets",40.757,-73.846,"NL","East"),T("Phillies",39.906,-75.166,"NL","East"),T("Nationals",38.873,-77.007,"NL","East"),
T("Cubs",41.948,-87.656,"NL","Central"),T("Reds",39.097,-84.507,"NL","Central"),T("Brewers",43.028,-87.971,"NL","Central"),T("Pirates",40.447,-80.006,"NL","Central"),T("Cardinals",38.622,-90.193,"NL","Central"),
T("Diamondbacks",33.445,-112.067,"NL","West"),T("Rockies",39.756,-104.994,"NL","West"),T("Dodgers",34.074,-118.240,"NL","West"),T("Padres",32.707,-117.157,"NL","West"),T("Giants",37.778,-122.389,"NL","West")],
"nba":[T("Celtics",42.366,-71.062,"East","Atlantic"),T("Nets",40.683,-73.975,"East","Atlantic"),T("Knicks",40.750,-73.993,"East","Atlantic"),T("76ers",39.901,-75.172,"East","Atlantic"),T("Raptors",43.643,-79.379,"East","Atlantic"),
T("Bulls",41.881,-87.674,"East","Central"),T("Cavaliers",41.497,-81.688,"East","Central"),T("Pistons",42.341,-83.055,"East","Central"),T("Pacers",39.764,-86.155,"East","Central"),T("Bucks",43.045,-87.917,"East","Central"),
T("Hawks",33.757,-84.396,"East","Southeast"),T("Hornets",35.225,-80.839,"East","Southeast"),T("Heat",25.781,-80.187,"East","Southeast"),T("Magic",28.539,-81.384,"East","Southeast"),T("Wizards",38.898,-77.021,"East","Southeast"),
T("Nuggets",39.749,-105.008,"West","Northwest"),T("Timberwolves",44.979,-93.276,"West","Northwest"),T("Thunder",35.463,-97.515,"West","Northwest"),T("Trail Blazers",45.532,-122.667,"West","Northwest"),T("Jazz",40.768,-111.901,"West","Northwest"),T("SuperSonics",47.6221,-122.354,"West","Northwest"),
T("Warriors",37.768,-122.388,"West","Pacific"),T("Clippers",33.945,-118.342,"West","Pacific"),T("Lakers",34.043,-118.267,"West","Pacific"),T("Suns",33.446,-112.071,"West","Pacific"),T("Kings",38.580,-121.500,"West","Pacific"),T("Las Vegas",36.1028,-115.1781,"West","Pacific"),
T("Mavericks",32.790,-96.810,"West","Southwest"),T("Rockets",29.751,-95.362,"West","Southwest"),T("Grizzlies",35.138,-90.051,"West","Southwest"),T("Pelicans",29.949,-90.082,"West","Southwest"),T("Spurs",29.427,-98.437,"West","Southwest")],
"mls":[T("Atlanta United",33.755,-84.401,"East","East"),T("Charlotte FC",35.226,-80.853,"East","East"),T("Chicago Fire",41.862,-87.617,"East","East"),T("FC Cincinnati",39.111,-84.522,"East","East"),T("Columbus Crew",39.969,-83.017,"East","East"),
T("DC United",38.868,-77.013,"East","East"),T("Inter Miami",26.193,-80.161,"East","East"),T("CF Montreal",45.563,-73.552,"East","East"),T("Nashville SC",36.131,-86.766,"East","East"),T("New England",42.091,-71.264,"East","East"),
T("NYCFC",40.829,-73.926,"East","East"),T("NY Red Bulls",40.737,-74.150,"East","East"),T("Orlando City",28.541,-81.389,"East","East"),T("Philadelphia Union",39.832,-75.378,"East","East"),T("Toronto FC",43.633,-79.418,"East","East"),
T("Austin FC",30.388,-97.719,"West","West"),T("Colorado Rapids",39.806,-104.892,"West","West"),T("FC Dallas",33.155,-96.835,"West","West"),T("Houston Dynamo",29.752,-95.352,"West","West"),T("LA Galaxy",33.864,-118.261,"West","West"),
T("LAFC",34.013,-118.285,"West","West"),T("Minnesota United",44.953,-93.165,"West","West"),T("Portland Timbers",45.522,-122.692,"West","West"),T("Real Salt Lake",40.583,-111.893,"West","West"),T("San Diego FC",32.783,-117.119,"West","West"),
T("San Jose",37.351,-121.925,"West","West"),T("Seattle Sounders",47.595,-122.332,"West","West"),T("Sporting KC",39.121,-94.824,"West","West"),T("St. Louis City",38.629,-90.211,"West","West"),T("Vancouver",49.277,-123.112,"West","West")],
}
SETPART_MAX=200000
def setpart(idxs,gs,D):
    groups=list(itertools.combinations(idxs,gs)); cost={g:sum(D[a][b] for a,b in itertools.combinations(g,2)) for g in groups}
    p=pulp.LpProblem("s",pulp.LpMinimize); z={g:pulp.LpVariable(f"z{k}",cat="Binary") for k,g in enumerate(groups)}
    p+=pulp.lpSum(cost[g]*z[g] for g in groups)
    for i in idxs: p+=pulp.lpSum(z[g] for g in groups if i in g)==1
    p.solve(pulp.PULP_CBC_CMD(msg=0)); return [list(g) for g in groups if z[g].value()>0.5]
def pmedian(idxs,gs,D):
    p=len(idxs)//gs; prob=pulp.LpProblem("pm",pulp.LpMinimize)
    y={j:pulp.LpVariable(f"y{j}",cat="Binary") for j in idxs}; x={(i,j):pulp.LpVariable(f"x_{i}_{j}",cat="Binary") for i in idxs for j in idxs}
    prob+=pulp.lpSum(D[i][j]*x[(i,j)] for i in idxs for j in idxs); prob+=pulp.lpSum(y[j] for j in idxs)==p
    for i in idxs: prob+=pulp.lpSum(x[(i,j)] for j in idxs)==1
    for j in idxs:
        prob+=x[(j,j)]==y[j]; prob+=pulp.lpSum(x[(i,j)] for i in idxs)==gs*y[j]
        for i in idxs: prob+=x[(i,j)]<=y[j]
    prob.solve(pulp.PULP_CBC_CMD(msg=0)); cl=defaultdict(list)
    for i in idxs:
        for j in idxs:
            if x[(i,j)].value()>0.5: cl[j].append(i); break
    return list(cl.values())
def opt(idxs,gs,D):
    if gs>=len(idxs): return [list(idxs)]
    return setpart(idxs,gs,D) if math.comb(len(idxs),gs)<=SETPART_MAX else pmedian(idxs,gs,D)
def opt_full(idxs,gs,D,K=16):
    if gs>=len(idxs): return [list(idxs)]
    if math.comb(len(idxs),gs)<=SETPART_MAX: return setpart(idxs,gs,D)
    pool=set()
    for seed in idxs:
        near=sorted([j for j in idxs if j!=seed],key=lambda j:D[seed][j])[:K]
        for c in itertools.combinations(near,gs-1): pool.add(tuple(sorted((seed,)+c)))
    pool=list(pool); cost={g:sum(D[a][b] for a,b in itertools.combinations(g,2)) for g in pool}
    p=pulp.LpProblem("pool",pulp.LpMinimize); z={g:pulp.LpVariable(f"z{k}",cat="Binary") for k,g in enumerate(pool)}
    p+=pulp.lpSum(cost[g]*z[g] for g in pool)
    for i in idxs: p+=pulp.lpSum(z[g] for g in pool if i in g)==1
    p.solve(pulp.PULP_CBC_CMD(msg=0)); return [list(g) for g in pool if z[g].value() and z[g].value()>0.5]
def maxcut2(idxs,D):
    half=len(idxs)//2; prob=pulp.LpProblem("mc",pulp.LpMaximize)
    x={i:pulp.LpVariable(f"x{i}",cat="Binary") for i in idxs}
    yv={}
    for a,b in itertools.combinations(idxs,2):
        v=pulp.LpVariable(f"y_{a}_{b}",cat="Binary"); yv[(a,b)]=v
        prob+=v<=x[a]+x[b]; prob+=v<=2-x[a]-x[b]
    prob+=pulp.lpSum(D[a][b]*yv[(a,b)] for a,b in yv); prob+=pulp.lpSum(x[i] for i in idxs)==half
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    g0=[i for i in idxs if x[i].value()<0.5]; g1=[i for i in idxs if x[i].value()>0.5]
    return [g0,g1]
def travel(groups,D): return sum(D[a][b] for g in groups for a,b in itertools.combinations(g,2))
def cen(grp,teams): return (sum(teams[i]["lat"] for i in grp)/len(grp), sum(teams[i]["lon"] for i in grp)/len(grp))
def _setpart_sizes(cand,idxs,sc,D):
    cost={g:sum(D[a][b] for a,b in itertools.combinations(g,2)) for g in cand}
    p=pulp.LpProblem("ms",pulp.LpMinimize); z={g:pulp.LpVariable(f"z{k}",cat="Binary") for k,g in enumerate(cand)}
    p+=pulp.lpSum(cost[g]*z[g] for g in cand)
    for i in idxs: p+=pulp.lpSum(z[g] for g in cand if i in g)==1
    for s,cnt in sc.items(): p+=pulp.lpSum(z[g] for g in cand if len(g)==s)==cnt
    p.solve(pulp.PULP_CBC_CMD(msg=0)); return [list(g) for g in cand if z[g].value() and z[g].value()>0.5]
def opt_multi(idxs,sizes,D):
    # divisions of given (possibly unequal) sizes; equal sizes route to the exact equal-size solver
    idxs=list(idxs)
    if len(set(sizes))==1: return opt(idxs,sizes[0],D)
    sc=Counter(sizes); cand=[g for s in sc for g in itertools.combinations(idxs,s)]
    return _setpart_sizes(cand,idxs,sc,D)
def opt_multi_full(idxs,sizes,D,K=16):
    idxs=list(idxs)
    if len(set(sizes))==1: return opt_full(idxs,sizes[0],D,K)
    sc=Counter(sizes)
    if sum(math.comb(len(idxs),s) for s in sc)<=SETPART_MAX:
        cand=[g for s in sc for g in itertools.combinations(idxs,s)]
    else:
        pool=set()
        for seed in idxs:
            near=sorted([j for j in idxs if j!=seed],key=lambda j:D[seed][j])[:K]
            for s in sc:
                for c in itertools.combinations(near,s-1): pool.add(tuple(sorted((seed,)+c)))
        cand=list(pool)
    return _setpart_sizes(cand,idxs,sc,D)

RESULT={}
for lg,teams in LEAGUES.items():
    n=len(teams); names=[t["name"] for t in teams]
    D=[[hav((teams[i]["lat"],teams[i]["lon"]),(teams[j]["lat"],teams[j]["lon"])) for j in range(n)] for i in range(n)]
    confs=sorted(set(t["conf"] for t in teams), key=lambda c:sum(teams[i]["lon"] for i in range(n) if teams[i]["conf"]==c)/sum(1 for t in teams if t["conf"]==c))
    ndiv=len(set((t["conf"],t["div"]) for t in teams)); dpc=ndiv//len(confs); gs=n//ndiv
    # A
    adiv=defaultdict(list)
    for i,t in enumerate(teams): adiv[(t["conf"],t["div"])].append(i)
    A=travel(adiv.values(),D)
    # B: keep conferences, re-optimize divisions at their real (possibly unequal) sizes
    confsizes={c:sorted(len(adiv[(cc,d)]) for (cc,d) in adiv if cc==c) for c in confs}
    leaguesizes=sorted(len(v) for v in adiv.values())
    Bg=[]
    for c in confs:
        ci=[i for i in range(n) if teams[i]["conf"]==c]
        Bg+=[(c,g) for g in opt_multi(ci,confsizes[c],D)]
    B=travel([g for _,g in Bg],D)
    # C: full optimum, split into 2 conferences by longitude (or maxcut if no subdiv)
    if gs>=n//2:  # MLS-like: no subdivisions, conferences are the unit
        g0,g1=maxcut2(list(range(n)),D); Cg=[g0,g1]; C=travel(Cg,D)
        west,east=(g0,g1) if cen(g0,teams)[1]<cen(g1,teams)[1] else (g1,g0)
        Cstruct=[("West",[("West",[names[i] for i in west])]),("East",[("East",[names[i] for i in east])])]
    else:
        Cg=opt_multi_full(list(range(n)),leaguesizes,D); C=travel(Cg,D)
        Cs=sorted(Cg,key=lambda g:cen(g,teams)[1]); half=len(Cs)//2
        west=Cs[:half]; east=Cs[half:]
        Cstruct=[("West",[("d%d"%k,[names[i] for i in g]) for k,g in enumerate(west)]),
                 ("East",[("d%d"%k,[names[i] for i in g]) for k,g in enumerate(east)])]
    Astruct=[(c,[(d,[names[i] for i in adiv[(c,d)]]) for (cc,d) in sorted(adiv) if cc==c]) for c in confs]
    Bbyc=defaultdict(list)
    for c,g in Bg: Bbyc[c].append([names[i] for i in g])
    Bstruct=[(c,[("d%d"%k,grp) for k,grp in enumerate(sorted(Bbyc[c],key=lambda gg:sum(teams[names.index(x)]["lon"] for x in gg)))]) for c in confs]
    RESULT[lg]={"n":n,"gs":gs,"confs":confs,"A":Astruct,"B":Bstruct,"C":Cstruct,
                "premium_pct":round((B-C)/A*100,1),"recover_B":round((A-B)/A*100,1),"recover_C":round((A-C)/A*100,1)}
    print(f"{lg:4s} n={n} divsize={gs} | A->B recover {(A-B)/A*100:4.1f}% | premium(B-C) {(B-C)/A*100:4.1f}%")
json.dump(RESULT,open("all_alignments.json","w"),indent=1)
print("saved all_alignments.json")
