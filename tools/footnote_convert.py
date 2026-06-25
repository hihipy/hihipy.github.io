#!/usr/bin/env python3
"""
Convert old-style numeric citations ([N] inline + a numbered references/sources
list with bare URLs) into Hugo/Goldmark Markdown footnotes ([^N] inline +
[^N]: definitions), matching the-pro-conference-premium.md.

Code is masked before any marker is touched, so array indices like c[0] inside
<script>/<style>/{{< chart >}}/code never convert.

Single file:
    python3 footnote_convert.py --check FILE      # report, write nothing
    python3 footnote_convert.py --write FILE       # convert in place (.backup-* kept)
Whole repo:
    python3 footnote_convert.py --scan  DIR        # classify every .md, write nothing
    python3 footnote_convert.py --write-all DIR     # convert every old-style file, skip the rest
"""
import argparse, re, sys, shutil, time, glob, os

# --- regions to protect from marker rewriting -----------------------------
MASK_PATTERNS = [
    re.compile(r'```.*?```', re.S),
    re.compile(r'`[^`]*`'),
    re.compile(r'<script\b.*?</script>', re.S | re.I),
    re.compile(r'<style\b.*?</style>', re.S | re.I),
    re.compile(r'<!--.*?-->', re.S),
    re.compile(r'{{<\s*chart\s*>}}.*?{{<\s*/\s*chart\s*>}}', re.S),
]
def mask(text):
    out = list(text)
    for pat in MASK_PATTERNS:
        for m in pat.finditer(text):
            for i in range(m.start(), m.end()):
                if out[i] != '\n':
                    out[i] = '\x00'
    return ''.join(out)

RUN = re.compile(r'(?<!\])(?<!\^)( ?)((?:\[\d{1,3}\])+)([.,;:]?)(?!\()')
HEADING = re.compile(r'^##\s+(References|Sources?|Notes?|Citations?|Bibliography|Footnotes?)\s*$', re.M)

def split_body_refs(text):
    m = HEADING.search(text)
    if not m:
        return text, None
    body = text[:m.start()].rstrip()
    body = re.sub(r'\n(?:\*\*\*|---|___)\s*$', '', body)
    return body + '\n', text[m.start():]

def convert_inline(body):
    masked = mask(body)
    edits = []
    for m in RUN.finditer(masked):
        nums = re.findall(r'\[(\d{1,3})\]', m.group(2))
        markers = ''.join(f'[^{n}]' for n in nums)
        edits.append((m.start(), m.end(), f'{m.group(3)}{markers}'))
    for s, e, r in sorted(edits, reverse=True):
        body = body[:s] + r + body[e:]
    return body, len(edits)

QUOTED = re.compile(r'"([^"]+)"')
URL = re.compile(r'(https?://\S+?)(?=[)\s]|$)')
def linkify_ref(text):
    text = text.strip()
    urls = URL.findall(text)
    if not urls:
        return text
    url = urls[-1]
    stripped = text[:text.rfind(url)].rstrip().rstrip('.').rstrip()
    qm = QUOTED.search(stripped)
    if qm:
        raw = qm.group(1)
        title = raw.rstrip(' .,;:')
        punct = raw[len(title):].strip()
        linked = stripped[:qm.start()] + f'[{title}]({url})' + punct + stripped[qm.end():]
    else:
        head = re.split(r'[.,]', stripped, maxsplit=1)[0].strip()
        linked = f'[{head}]({url})' + stripped[len(head):]
    linked = linked.rstrip()
    if not linked.endswith(('.', '?', '!')):
        linked += '.'
    return linked

def convert_refs(refs_block, linkify=True):
    lines = refs_block.splitlines()
    preamble, defs = [], []
    item = re.compile(r'^\s*(\d{1,3})\.\s+(.*\S)\s*$')
    cur_n, cur_buf = None, []
    def flush():
        nonlocal cur_n, cur_buf
        if cur_n is not None:
            body = ' '.join(cur_buf).strip()
            defs.append((cur_n, linkify_ref(body) if linkify else body))
        cur_n, cur_buf = None, []
    for ln in lines[1:]:
        m = item.match(ln)
        if m:
            flush(); cur_n, cur_buf = int(m.group(1)), [m.group(2)]
        elif cur_n is not None and ln.strip():
            cur_buf.append(ln.strip())
        elif cur_n is None and ln.strip():
            preamble.append(ln.strip())
    flush()
    return defs, preamble

def build(text, linkify=True):
    body, refs_block = split_body_refs(text)
    new_body, n_inline = convert_inline(body)
    if refs_block is None:
        return new_body, n_inline, 0, []
    defs, preamble = convert_refs(refs_block, linkify=linkify)
    out = new_body.rstrip() + '\n\n'
    if preamble:
        out += '\n'.join(f'*{p}*' for p in preamble) + '\n\n'
    out += '\n'.join(f'[^{n}]: {t}' for n, t in defs) + '\n'
    return out, n_inline, len(defs), preamble

# --- classification for the sweep -----------------------------------------
def classify(text):
    has_fn = bool(re.search(r'^\[\^[^\]]+\]:', text, re.M))
    nums = len(re.findall(r'\[\d{1,3}\](?!\()(?!:)', mask(text)))
    has_head = bool(HEADING.search(text))
    if has_fn and nums == 0:
        return 'footnotes'        # already converted
    if nums > 0 and has_head:
        return 'old-style'        # convertible
    if nums > 0:
        return 'numeric-no-list'  # has [N] but no refs heading: needs a look
    return 'none'

def reconcile(out):
    body = re.sub(r'^\[\^\d+\]:.*$', '', out, flags=re.M)
    used = set(re.findall(r'\[\^(\d+)\]', body))
    deff = set(re.findall(r'^\[\^(\d+)\]:', out, re.M))
    return used, deff

def write_one(path, linkify, dry=False):
    text = open(path, encoding='utf-8').read()
    out, ni, nd, _ = build(text, linkify=linkify)
    used, deff = reconcile(out)
    ok = used == deff
    if not dry:
        bak = f"{path}.backup-{time.strftime('%Y%m%d-%H%M%S')}"
        shutil.copy2(path, bak)
        open(path, 'w', encoding='utf-8').write(out)
    return ni, nd, used, deff, ok

def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--check'); g.add_argument('--write')
    g.add_argument('--scan'); g.add_argument('--write-all')
    ap.add_argument('--no-linkify', action='store_true')
    a = ap.parse_args()
    linkify = not a.no_linkify

    if a.scan or a.write_all:
        root = a.scan or a.write_all
        files = sorted(f for f in glob.glob(os.path.join(root, '**', '*.md'), recursive=True)
                       if '/tags/' not in f)
        converted = skipped = 0
        for f in files:
            kind = classify(open(f, encoding='utf-8').read())
            short = os.path.relpath(f, root)
            if kind == 'old-style':
                if a.write_all:
                    ni, nd, used, deff, ok = write_one(f, linkify)
                    flag = 'OK' if ok else f'MISMATCH used={sorted(used)} def={sorted(deff)}'
                    print(f"  CONVERT  {short:50} {ni:>3} markers, {nd:>2} notes  [{flag}]")
                    converted += 1
                else:
                    ni, nd, used, deff, ok = write_one(f, linkify, dry=True)
                    print(f"  old-style  {short:48} -> {ni} markers, {nd} notes")
                    converted += 1
            elif kind == 'numeric-no-list':
                print(f"  REVIEW   {short:50} has [N] but no refs heading")
                skipped += 1
            elif kind == 'footnotes':
                print(f"  footnotes  {short:48} already converted, skip")
                skipped += 1
            else:
                skipped += 1
        verb = 'converted' if a.write_all else 'would convert'
        print(f"\n{verb} {converted} file(s); skipped {skipped}; scanned {len(files)}")
        return

    path = a.check or a.write
    ni, nd, used, deff, ok = write_one(path, linkify, dry=bool(a.check))
    print(f"  inline runs converted : {ni}")
    print(f"  definitions written   : {nd}")
    print(f"  ids used / defined    : {len(used)} / {len(deff)}")
    if used - deff: print(f"  !! used but undefined : {sorted(used-deff, key=int)}")
    if deff - used: print(f"  .. defined but unused : {sorted(deff-used, key=int)}")
    if a.write:
        print(f"  wrote {path}")

if __name__ == '__main__':
    main()
