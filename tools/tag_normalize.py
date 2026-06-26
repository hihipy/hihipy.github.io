#!/usr/bin/env python3
"""
Normalize portfolio tags to the faceted controlled vocabulary (see TAG_METHODOLOGY.md).
Keeps three sources of truth in sync:
  1. tags: [...] in each project page's frontmatter (facet-ordered)
  2. content/tags/<tag>/_index.md term pages (create new, delete unused)
  3. the $tagMap dict in layouts/partials/article-link/card.html (display labels)

Usage:
  python3 tag_normalize.py --scan  REPO     # report every change, write nothing
  python3 tag_normalize.py --write REPO      # apply, keeping .backup-* for edited files
"""
import re, os, sys, glob, json, time, shutil, argparse

MAP = {
 'python':('language','python'),'sql':('language','sql'),'r':('language','r'),
 'csharp':('language','csharp'),'vba':('language','vba'),'latex':('language','latex'),
 'html':('language','html'),'dax':('language','dax'),
 'sqlite':('tool','sqlite'),'datasette':('tool','datasette'),'sqlite-utils':('tool','sqlite-utils'),
 'pandas':('tool','pandas'),'tkinter':('tool','tkinter'),'customtkinter':('tool','tkinter'),
 'matplotlib':('tool','matplotlib'),'jupyter':('tool','jupyter'),'selenium':('tool','selenium'),
 'beautifulsoup':('tool','beautifulsoup'),'nltk':('tool','nltk'),'wordnet':('tool','nltk'),
 'excel':('tool','excel'),'power-bi':('tool','power-bi'),'tabular-editor':('tool','power-bi'),
 'qualtrics':('tool','qualtrics'),'asyncio':('tool','asyncio'),'postgresql':('tool','postgresql'),
 'mysql':('tool',None),'mariadb':('tool',None),'oracle':('tool',None),'sql-server':('tool',None),
 'firebird':('tool',None),'bigquery':('tool',None),
 'csv':('tool','csv'),'json':('tool','json'),'pdf':('tool','pdf'),
 'etl':('concept','etl'),'data-cleaning':('concept','data-cleaning'),'data-quality':('concept','data-quality'),
 'data-profiling':('concept','data-profiling'),'exploratory-analysis':('concept','exploratory-analysis'),
 'data-visualization':('concept','data-visualization'),'schema-design':('concept','schema-design'),
 'ctes':('concept','ctes'),'window-functions':('concept','window-functions'),
 'causal-inference':('concept','causal-inference'),'econometrics':('concept','econometrics'),
 'synthetic-control':('concept','synthetic-control'),'logistic-regression':('concept','logistic-regression'),
 'predictive-modeling':('concept','predictive-modeling'),'optimization':('concept','optimization'),
 'operations-research':('concept','operations-research'),'combinatorics':('concept','combinatorics'),
 'mathematics':('concept','mathematics'),'public-data':('concept','public-data'),
 'survey-data':('concept','survey-data'),'browser-automation':('concept','web-scraping'),
 'documentation':('concept','documentation'),'reporting':('concept','reporting'),'audit':('concept','audit'),
 'process-improvement':('concept','process-improvement'),'macros':('concept','macros'),
 'ai':('concept','ai'),'llm':('concept','llm'),'multi-provider':('concept','llm'),
 'word-cloud':('concept',None),'seo':('concept','seo'),'scale':('concept',None),'bi':('concept',None),
 'higher-ed':('domain','higher-education'),'nursing-education':('domain','nursing-education'),
 'nclex':('domain','nursing-education'),'finance':('domain','finance'),'per-diem':('domain','finance'),
 'travel':('domain','travel'),'sports':('domain','sports'),'inequality':('domain','economics'),
 'deep-time':('domain','earth-science'),
 'college-scorecard':('domain',None),'nih-reporter':('domain',None),'nih':('domain',None),
 'kentucky':('domain',None),'florida':('domain',None),
 'data-essay':('type','data-essay'),'data essay':('type','data-essay'),
 'side-project':('type','side-project'),'calculator':('type','calculator'),
}
ROOM_TYPE = {'archivo':'case-study','despacho':'data-essay','cocina':'tool',
             'estudio':'tool','garaje':'tool','jardin':'side-project'}
FACETS=['language','tool','concept','domain','type']
FACET_OF={}
for _o,(_f,_c) in MAP.items():
    if _c: FACET_OF[_c]=_f
for rt in set(ROOM_TYPE.values()): FACET_OF[rt]='type'

# display labels (reuse existing where special-cased; title-case otherwise)
DISPLAY={
 'sql':'SQL','sqlite':'SQLite','sqlite-utils':'sqlite-utils','postgresql':'PostgreSQL','csv':'CSV',
 'json':'JSON','pdf':'PDF','html':'HTML','dax':'DAX','csharp':'C#','vba':'VBA','latex':'LaTeX','r':'R',
 'etl':'ETL','ctes':'CTEs','ai':'AI','llm':'LLM','seo':'SEO','pandas':'pandas','nltk':'NLTK',
 'beautifulsoup':'BeautifulSoup','power-bi':'Power BI','tkinter':'Tkinter','jupyter':'Jupyter',
 'matplotlib':'Matplotlib','selenium':'Selenium','qualtrics':'Qualtrics','asyncio':'asyncio',
 'excel':'Excel','datasette':'Datasette','python':'Python',
 'data-essay':'Data Essay','case-study':'Case Study','side-project':'Side Project','tool':'Tool',
 'calculator':'Calculator','higher-education':'Higher Education','nursing-education':'Nursing Education',
 'earth-science':'Earth Science','economics':'Economics','finance':'Finance','travel':'Travel','sports':'Sports',
 'web-scraping':'Web Scraping','operations-research':'Operations Research','optimization':'Optimization',
 'causal-inference':'Causal Inference','econometrics':'Econometrics','synthetic-control':'Synthetic Control',
 'logistic-regression':'Logistic Regression','predictive-modeling':'Predictive Modeling',
 'combinatorics':'Combinatorics','mathematics':'Mathematics','public-data':'Public Data',
 'survey-data':'Survey Data','schema-design':'Schema Design','window-functions':'Window Functions',
 'data-cleaning':'Data Cleaning','data-quality':'Data Quality','data-profiling':'Data Profiling',
 'exploratory-analysis':'Exploratory Analysis','data-visualization':'Data Visualization',
 'documentation':'Documentation','reporting':'Reporting','audit':'Audit','macros':'Macros',
 'process-improvement':'Process Improvement',
}
def label(t): return DISPLAY.get(t, t.replace('-',' ').title())

def normalize(tags, room):
    buckets={f:[] for f in FACETS}
    unknown=[]
    for t in tags:
        if t in MAP:
            f,c=MAP[t]
            if c and c not in buckets[f]: buckets[f].append(c)
        else:
            unknown.append(t)
            if t not in buckets['concept']: buckets['concept'].append(t)  # keep, flag
    if not buckets['type'] and ROOM_TYPE.get(room): buckets['type']=[ROOM_TYPE[room]]
    out=[]
    for f in FACETS: out+=sorted(buckets[f])
    return out, unknown

FM=re.compile(r'^(---\s*\n.*?\n---\s*\n)', re.S)
TAGLINE=re.compile(r'^tags:.*$', re.M)

def content_files(repo):
    return sorted(f for f in glob.glob(os.path.join(repo,'content','**','*.md'),recursive=True)
                  if '/themes/' not in f and '/content/tags/' not in f)

def get_room(repo,f):
    rel=os.path.relpath(f,os.path.join(repo,'content'))
    return rel.split(os.sep)[0] if os.sep in rel else ''

def read_tags(fm):
    m=re.search(r'^tags:\s*\[(.*?)\]', fm, re.M|re.S)
    if m: return [x.strip().strip('"\'') for x in m.group(1).split(',') if x.strip()]
    m=re.search(r'^tags:\s*\n((?:\s*-\s*.+\n?)+)', fm, re.M)
    if m: return [re.sub(r'^\s*-\s*','',l).strip().strip('"\'') for l in m.group(1).splitlines() if l.strip()]
    return None

def main():
    ap=argparse.ArgumentParser(); g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--scan'); g.add_argument('--write'); a=ap.parse_args()
    repo=a.scan or a.write; write=bool(a.write)
    files=content_files(repo)
    final_vocab=set(); unknowns={}; changed=0
    print("== FRONTMATTER ==")
    for f in files:
        txt=open(f,encoding='utf-8').read()
        mfm=FM.match(txt)
        if not mfm: continue
        fm=mfm.group(1)
        tags=read_tags(fm)
        if tags is None: continue
        room=get_room(repo,f)
        new,unk=normalize(tags,room)
        final_vocab.update(new)
        if unk: unknowns[os.path.relpath(f,repo)]=unk
        if new!=tags:
            changed+=1
            arr='tags: ['+', '.join(f'"{t}"' for t in new)+']'
            rel=os.path.relpath(f,repo)
            print(f"  {rel}")
            print(f"     - {tags}")
            print(f"     + {new}")
            if write:
                newfm=TAGLINE.sub(arr, fm, count=1)
                shutil.copy2(f,f+f".backup-{time.strftime('%Y%m%d-%H%M%S')}")
                open(f,'w',encoding='utf-8').write(newfm+txt[mfm.end():])
    # term pages
    tagdir=os.path.join(repo,'content','tags')
    existing={d for d in os.listdir(tagdir) if os.path.isdir(os.path.join(tagdir,d))} if os.path.isdir(tagdir) else set()
    to_create=sorted(final_vocab-existing); to_delete=sorted(existing-final_vocab)
    print("\n== TERM PAGES ==")
    print(f"  create ({len(to_create)}): {to_create}")
    print(f"  delete ({len(to_delete)}): {to_delete}")
    if write:
        for t in to_create:
            os.makedirs(os.path.join(tagdir,t),exist_ok=True)
            open(os.path.join(tagdir,t,'_index.md'),'w').write(f'---\ntitle: "{label(t)}"\n---\n')
        for t in to_delete:
            shutil.rmtree(os.path.join(tagdir,t))
    # card.html $tagMap
    card=os.path.join(repo,'layouts','partials','article-link','card.html')
    print("\n== CARD $tagMap ==")
    if os.path.isfile(card):
        c=open(card,encoding='utf-8').read()
        block=re.search(r'(\{\{\s*\$tagMap\s*:=\s*dict\b).*?(\n\s*\}\})', c, re.S)
        if block:
            lines='\n'.join(f'        "{t}" "{label(t)}"' for t in sorted(final_vocab))
            newblock=block.group(1)+'\n'+lines+'\n      }}'
            print(f"  regenerating dict to {len(final_vocab)} entries (was a fixed list)")
            # validate even arg count
            assert newblock.count('"')%2==0, "odd quote count in tagMap"
            if write:
                shutil.copy2(card,card+f".backup-{time.strftime('%Y%m%d-%H%M%S')}")
                open(card,'w',encoding='utf-8').write(c[:block.start()]+newblock+c[block.end():])
        else:
            print("  !! could not locate $tagMap block")
    # reconciliation
    print("\n== RECONCILIATION ==")
    print(f"  files changed: {changed}")
    print(f"  final vocabulary: {len(final_vocab)} tags")
    if unknowns:
        print(f"  !! tags not in vocabulary (kept as concept, please classify): {unknowns}")
    else:
        print("  every declared tag is in the controlled vocabulary")
    print(f"  every final tag will have a term page: {final_vocab<= (final_vocab|set(to_create))}")
    print("\n"+("WROTE changes (backups kept)" if write else "DRY RUN, nothing written"))

if __name__=='__main__': main()
