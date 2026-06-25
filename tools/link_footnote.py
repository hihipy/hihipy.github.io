#!/usr/bin/env python3
"""
Convert genuine SOURCE/dataset inline links into [^id] footnotes (pro-conference
style), leaving tool, glossary, action, badge, internal, and self links inline.
Source links are recognised by a curated domain allowlist; ambiguous domains
(Wikipedia, standards bodies) are reported for manual review, never auto-converted.
"""
import re, sys, glob, os, time, shutil, argparse

# domain -> publisher (authority/dataset sources only)
SOURCE = {
 'reporter.nih.gov':'NIH RePORTER', 'report.nih.gov':'NIH', 'grants.nih.gov':'NIH', 'nih.gov':'NIH',
 'collegescorecard.ed.gov':'U.S. Department of Education', 'sites.ed.gov':'U.S. Department of Education',
 'studentprivacy.ed.gov':'U.S. Department of Education', 'ncsbn.org':'NCSBN',
 'mixtape.scunning.com':'Scott Cunningham', 'hhs.gov':'U.S. Dept. of Health and Human Services',
 'brimr.org':'Blue Ridge Institute for Medical Research', 'ukhealthcare.uky.edu':'University of Kentucky',
 'sabr.org':'SABR', 'nba.com':'NBA',
}
REVIEW_DOMAINS = {'en.wikipedia.org','w3.org','webaim.org','archive.org','creativecommons.org'}

MASK=[re.compile(r'```.*?```',re.S),re.compile(r'`[^`]*`'),
      re.compile(r'<script\b.*?</script>',re.S|re.I),re.compile(r'<style\b.*?</style>',re.S|re.I),
      re.compile(r'{{<\s*chart\s*>}}.*?{{<\s*/\s*chart\s*>}}',re.S)]
def masked_spans(t):
    spans=[]
    for p in MASK:
        spans += [(m.start(),m.end()) for m in p.finditer(t)]
    return spans
def in_spans(i,spans): return any(s<=i<e for s,e in spans)

LINK=re.compile(r'(?<!\!)\[([^\]]+)\]\((https?://[^)]+)\)')
def domain(u): return re.sub(r'^https?://(www\.)?','',u).split('/')[0]
def slugify(t):
    t=re.sub(r'\*|`|"','',t)
    s=re.sub(r'[^a-z0-9]+','-',t.lower()).strip('-')
    return (s or 'src')[:32]

def convert(text):
    spans=masked_spans(text)
    edits=[]; defs=[]; review=[]; used=set()
    for m in LINK.finditer(text):
        if in_spans(m.start(),spans): continue
        txt,url=m.group(1),m.group(2)
        if '{{<' in txt: continue                  # badge chips
        d=domain(url)
        if d in REVIEW_DOMAINS:
            review.append((txt,url)); continue
        if d not in SOURCE: continue               # tool/gloss/action/self/internal -> leave inline
        slug=slugify(txt); base=slug; k=2
        while slug in used: slug=f"{base}-{k}"; k+=1
        used.add(slug)
        pub=SOURCE[d]
        cleantxt=re.sub(r'\*|`','',txt).lower()
        deftext=f"[{txt}]({url})" + (f", {pub}." if pub and pub.lower() not in cleantxt else ".")
        defs.append((slug,deftext))
        edits.append((m.start(),m.end(),f"{txt}[^{slug}]"))
    for s,e,r in sorted(edits,reverse=True):
        text=text[:s]+r+text[e:]
    if defs:
        text=text.rstrip()+"\n\n"+"\n".join(f"[^{s}]: {t}" for s,t in defs)+"\n"
    return text, defs, review

def main():
    ap=argparse.ArgumentParser()
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--scan'); g.add_argument('--write')   # both take a DIR or FILE
    a=ap.parse_args()
    target=a.scan or a.write
    if os.path.isdir(target):
        files=sorted(f for f in glob.glob(os.path.join(target,'**','*.md'),recursive=True)
                     if '/tags/' not in f)
    else:
        files=[target]
    tot_def=tot_rev=0
    for f in files:
        text=open(f,encoding='utf-8').read()
        out,defs,review=convert(text)
        if not defs and not review: continue
        short=os.path.relpath(f,target) if os.path.isdir(target) else os.path.basename(f)
        print(f"\n{short}")
        for s,t in defs:    print(f"   FOOTNOTE  {t}")
        for txt,url in review: print(f"   review?   [{txt[:46]}] {domain(url)}")
        tot_def+=len(defs); tot_rev+=len(review)
        if a.write and defs:
            shutil.copy2(f,f+f".backup-{time.strftime('%Y%m%d-%H%M%S')}")
            open(f,'w',encoding='utf-8').write(out)
    print(f"\n=== {tot_def} source links -> footnotes; {tot_rev} flagged for review ===")
    if a.write: print("(written; backups kept)")

if __name__=='__main__': main()
