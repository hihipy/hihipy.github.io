#!/usr/bin/env python3
"""
audit_figures.py  -  Figure contrast auditor and auto-fixer for pgbd.casa

Walks every Chart.js figure in content/**/*.md, measures WCAG contrast for each
series color AND each text element (title / axis title / tick labels / legend)
against the actual canvas color in BOTH light and dark themes, then optionally
fixes the safe cases in place.

Mechanism-aware (this is what makes the verdicts honest):

  * Per-page swap adapter (BUG-019). Files carrying the inline adapter
    (signature: Chart.getChart) swap #0969DA<->#79C0FF and #000000<->#FFFFFF at
    runtime, so those hexes are graded against their dark-rendered value ONLY in
    files that actually run the adapter. Everywhere else the raw hex is graded
    against the dark canvas. So an intentional #000000 slope series in an
    adapter page is NOT a failure, and #0969DA off an adapter page is graded at
    its true 3.44:1 dark, not an optimistic swapped value.

  * Theme-aware text/grid forms are APPROVED, not flagged. A text/grid color
    set to window.__tc() / window.__gc() (first-trillion pattern) or simply
    absent (driven by theme-aware Chart.defaults, BUG-035) resolves to the
    neutral-700 / neutral-200 theme colors, which are AAA in both modes. Only a
    HARDCODED hex in a title/tick/legend/grid slot is a BUG-034 violation; the
    tool reports its real two-mode contrast and offers to strip it.

  * Inline accept markers. A `// audit-ok` or `// audit-accept` comment on or
    just above a dataset/line moves its colors to a separate ACCEPTED section
    (the BUG-022 "document the choice inline" rule, made machine-checkable).

Theme model: github scheme. Blowfish defines the neutral scale in :root and
reverses it under .dark (50<->900, 200<->700, ...). Light canvas = neutral
DEFAULT (#FFFFFF, the card surface). Dark canvas = reversed DEFAULT (#0F172A).
Override with --light-canvas/--dark-canvas or re-derive with --scheme-css.

Pure stdlib, Python 3.8+.

Usage:
  python3 tools/audit_figures.py                 # audit content/, report only
  python3 tools/audit_figures.py --self-test     # theme + palette tables
  python3 tools/audit_figures.py --fix           # strip hardcoded text colors;
                                                  #   remap genuinely-invisible series
  python3 tools/audit_figures.py --fix-all       # also remap FAIL series to nearest approved
  python3 tools/audit_figures.py --json          # machine-readable findings
Exit code is non-zero while any unresolved FAIL or hardcoded text color remains.
"""

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime

# ----------------------------------------------------------------------------
# Color math (WCAG 2.1) + perceptual distance
# ----------------------------------------------------------------------------

def _parse_color(s):
    s = s.strip().strip("'\"").strip()
    m = re.fullmatch(r'#([0-9a-fA-F]{3,8})', s)
    if m:
        h = m.group(1)
        if len(h) == 3:
            r, g, b = (int(c * 2, 16) for c in h); return (r, g, b, 1.0)
        if len(h) == 4:
            r, g, b, a = (int(c * 2, 16) for c in h); return (r, g, b, a / 255)
        if len(h) == 6:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0)
        if len(h) == 8:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16) / 255)
    m = re.fullmatch(r'rgba?\(([^)]*)\)', s)
    if m:
        parts = [p.strip() for p in m.group(1).split(',')]
        if len(parts) in (3, 4):
            try:
                r, g, b = (int(round(float(p))) for p in parts[:3])
                a = float(parts[3]) if len(parts) == 4 else 1.0
                return (r, g, b, a)
            except ValueError:
                return None
    return None


def _to_hex(rgb):
    return '#{:02X}{:02X}{:02X}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


def _lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def _luminance(rgb):
    return 0.2126 * _lin(rgb[0]) + 0.7152 * _lin(rgb[1]) + 0.0722 * _lin(rgb[2])


def contrast(fg, bg):
    l1, l2 = _luminance(fg), _luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def grade(ratio):
    if ratio >= 7.0: return 'AAA-text'
    if ratio >= 4.5: return 'AA-text'
    if ratio >= 3.0: return 'AA-large'
    return 'FAIL'


def _srgb_to_lab(rgb):
    def f_lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f_lin(rgb[0]), f_lin(rgb[1]), f_lin(rgb[2]))
    x = (r * 0.4124 + g * 0.3576 + b * 0.1805) / 0.95047
    y = (r * 0.2126 + g * 0.7152 + b * 0.0722)
    z = (r * 0.0193 + g * 0.1192 + b * 0.9505) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else (7.787 * t + 16 / 116)
    fx, fy, fz = f(x), f(y), f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def de76(rgb1, rgb2):
    a, b = _srgb_to_lab(rgb1), _srgb_to_lab(rgb2)
    return sum((a[i] - b[i]) ** 2 for i in range(3)) ** 0.5


# ----------------------------------------------------------------------------
# Theme model
# ----------------------------------------------------------------------------

GH_NEUTRAL_LIGHT = {
    'DEFAULT': (255, 255, 255),
    50: (248, 250, 252), 100: (241, 245, 249), 200: (226, 232, 240),
    300: (203, 213, 225), 400: (148, 163, 184), 500: (100, 116, 139),
    600: (71, 85, 105), 700: (51, 57, 65), 800: (20, 25, 31), 900: (15, 23, 42),
}
REVERSE = {50: 900, 100: 800, 200: 700, 300: 600, 400: 500,
           500: 400, 600: 300, 700: 200, 800: 100, 900: 50, 'DEFAULT': 900}


class Theme:
    def __init__(self, neutral_light=None, light_canvas=None, dark_canvas=None):
        self.neutral = dict(neutral_light or GH_NEUTRAL_LIGHT)
        self.light_canvas = light_canvas or self.neutral['DEFAULT']
        self.dark_canvas = dark_canvas or self.neutral[REVERSE['DEFAULT']]

    def n(self, step, dark):
        return self.neutral[REVERSE[step]] if dark else self.neutral[step]

    @property
    def light_text(self): return self.n(700, False)
    @property
    def dark_text(self): return self.n(700, True)
    @property
    def light_grid(self): return self.n(200, False)
    @property
    def dark_grid(self): return self.n(200, True)


def load_scheme_css(path):
    txt = open(path, encoding='utf-8').read()
    out = dict(GH_NEUTRAL_LIGHT)
    for m in re.finditer(r'--color-neutral(?:-(\d+))?\s*:\s*([0-9]+)\s*,\s*([0-9]+)\s*,\s*([0-9]+)', txt):
        step = int(m.group(1)) if m.group(1) else 'DEFAULT'
        out[step] = (int(m.group(2)), int(m.group(3)), int(m.group(4)))
    return out


DARK_SWAP = {'#0969DA': '#79C0FF', '#000000': '#FFFFFF'}
APPROVED = ['#0969DA', '#BF8700', '#CF222E', '#BF3989', '#1A7F37', '#8250DF']
MARK_FLOOR = 3.0
THEME_AWARE_RE = re.compile(r'window\.__\w+\(\)|--color-|getComputedStyle|getPropertyValue')
ADAPTER_SIGNATURE = re.compile(r'Chart\.getChart')
ACCEPT_RE = re.compile(r'audit-(?:ok|accept)')


def rendered_in_dark(hexv, has_adapter):
    return DARK_SWAP.get(hexv.upper(), hexv) if has_adapter else hexv


def series_ratios(hexv, theme, has_adapter):
    rgb = _parse_color(hexv)[:3]
    lr = contrast(rgb, theme.light_canvas)
    dhex = rendered_in_dark(hexv, has_adapter)
    dr = contrast(_parse_color(dhex)[:3], theme.dark_canvas)
    return lr, dr, dhex


def best_replacement(orig_hex, theme, used, has_adapter):
    orig_rgb = _parse_color(orig_hex)[:3]
    used_up = {u.upper() for u in used}
    cands = []
    for c in APPROVED:
        if c.upper() in used_up:
            continue
        lr, dr, _ = series_ratios(c, theme, has_adapter)
        if lr >= MARK_FLOOR and dr >= MARK_FLOOR:
            cands.append((de76(orig_rgb, _parse_color(c)[:3]), c))
    if not cands:
        return None
    if orig_hex.upper() == '#000000' and any(c == '#BF8700' for _, c in cands):
        return '#BF8700'
    cands.sort(key=lambda t: t[0])
    return cands[0][1]


# ----------------------------------------------------------------------------
# Parsing
# ----------------------------------------------------------------------------

CHART_BLOCK = re.compile(r'{{<\s*chart\s*>}}(.*?){{<\s*/chart\s*>}}', re.DOTALL)
LITVAL = r"""('[^']*'|"[^"]*"|rgba?\([^)]*\)|#[0-9A-Fa-f]{3,8})"""
ANYVAL = r"""('[^']*'|"[^"]*"|rgba?\([^)]*\)|#[0-9A-Fa-f]{3,8}|[A-Za-z_$][\w.$]*\([^)]*\)|[A-Za-z_$][\w.$]*)"""

RE_BARE_COLOR = re.compile(
    r"(?P<lead>,?\s*)(?<![A-Za-z0-9_])color\s*:\s*(?P<val>" + ANYVAL + r")(?P<trail>\s*,?)")
RE_SERIES_SINGLE = re.compile(r"(?P<key>[A-Za-z]+Color)\s*:\s*(?P<val>" + LITVAL + r")")
RE_SERIES_ARRAY = re.compile(r"(?P<key>[A-Za-z]+Color)\s*:\s*\[(?P<arr>[^\]]*)\]")
RE_LITERAL = re.compile(LITVAL)
RE_TYPE = re.compile(r"\btype\s*:\s*'([a-zA-Z]+)'")


def _line_of(text, pos):
    return text.count('\n', 0, pos) + 1


def _classify_bare(block, rel_pos):
    window = block[max(0, rel_pos - 90):rel_pos]
    label = {'ticks': 'axis-tick', 'grid': 'grid', 'labels': 'legend', 'title': 'title'}
    best_k, best_pos = None, -1
    for k in label:
        p = window.rfind(k)
        if p > best_pos:
            best_k, best_pos = k, p
    return label.get(best_k, 'axis-text')


def _nearest_type(block, rel_pos, chart_type):
    best = chart_type
    for m in RE_TYPE.finditer(block):
        if m.start() < rel_pos:
            best = m.group(1)
        else:
            break
    return best or 'chart'


def _accepted_near(block, rel_pos):
    line_end = block.find('\n', rel_pos)
    line_end = line_end if line_end != -1 else len(block)
    line_start = block.rfind('\n', 0, rel_pos) + 1
    prev_start = block.rfind('\n', 0, line_start - 1) + 1
    return bool(ACCEPT_RE.search(block[prev_start:line_end]))


class Finding:
    __slots__ = ('file', 'line', 'chart_idx', 'role', 'literal', 'hexnorm',
                 'is_fill', 'mark', 'start', 'end', 'strip_repl',
                 'theme_aware', 'accepted', 'has_adapter')

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k))


def scan_text(text, path):
    findings = []
    has_adapter = bool(ADAPTER_SIGNATURE.search(text))
    for ci, bm in enumerate(CHART_BLOCK.finditer(text), start=1):
        block = bm.group(1)
        base = bm.start(1)
        tm = RE_TYPE.search(block)
        chart_type = tm.group(1) if tm else 'chart'

        for m in RE_BARE_COLOR.finditer(block):
            val = m.group('val')
            theme_aware = bool(THEME_AWARE_RE.search(val)) or _parse_color(val) is None
            lead, trail = m.group('lead'), m.group('trail')
            repl = ',' if (',' in lead and ',' in trail) else ''
            findings.append(Finding(
                file=path, line=_line_of(text, base + m.start()), chart_idx=ci,
                role=_classify_bare(block, m.start()), literal=val,
                hexnorm=(_to_hex(_parse_color(val)) if not theme_aware else None),
                is_fill=False, mark='text', start=base + m.start(), end=base + m.end(),
                strip_repl=repl, theme_aware=theme_aware,
                accepted=_accepted_near(block, m.start()), has_adapter=has_adapter))

        array_spans = []
        for m in RE_SERIES_ARRAY.finditer(block):
            array_spans.append((m.start(), m.end()))
            arr_base = base + m.start('arr')
            for lm in RE_LITERAL.finditer(m.group('arr')):
                c = _parse_color(lm.group(0))
                if not c:
                    continue
                findings.append(_series_finding(
                    text, path, ci, m.group('key'), lm.group(0), c,
                    arr_base + lm.start(), arr_base + lm.end(),
                    _nearest_type(block, m.start(), chart_type),
                    _accepted_near(block, m.start()), has_adapter))

        for m in RE_SERIES_SINGLE.finditer(block):
            if any(a <= m.start() < b for a, b in array_spans):
                continue
            c = _parse_color(m.group('val'))
            if not c:
                continue
            findings.append(_series_finding(
                text, path, ci, m.group('key'), m.group('val'), c,
                base + m.start('val'), base + m.end('val'),
                _nearest_type(block, m.start(), chart_type),
                _accepted_near(block, m.start()), has_adapter))
    return findings


def _series_finding(text, path, ci, key, literal, parsed, start, end, mark, accepted, has_adapter):
    return Finding(
        file=path, line=_line_of(text, start), chart_idx=ci,
        role=('series-fill' if parsed[3] < 0.999 else 'series'),
        literal=literal, hexnorm=_to_hex(parsed), is_fill=parsed[3] < 0.999,
        mark=mark, start=start, end=end, strip_repl=None,
        theme_aware=False, accepted=accepted, has_adapter=has_adapter)


# ----------------------------------------------------------------------------
# Evaluation + reporting
# ----------------------------------------------------------------------------

def rendered_dark_text(rgb, has_adapter):
    if has_adapter:
        sw = DARK_SWAP.get(_to_hex(rgb).upper())
        if sw:
            return _parse_color(sw)[:3]
    return rgb[:3]


def evaluate(findings, theme):
    rows = []
    for f in findings:
        if f.role.startswith('series'):
            hexv = f.hexnorm
            lr, dr, dhex = series_ratios(hexv, theme, f.has_adapter)
            rows.append({'f': f, 'kind': 'series', 'hex': hexv, 'dark_hex': dhex,
                         'lr': lr, 'dr': dr, 'fail': lr < MARK_FLOOR or dr < MARK_FLOOR})
        elif f.theme_aware:
            rows.append({'f': f, 'kind': 'text-themed',
                         'lr': contrast(theme.light_text, theme.light_canvas),
                         'dr': contrast(theme.dark_text, theme.dark_canvas), 'fail': False})
        else:
            rgb = _parse_color(f.literal)
            rows.append({'f': f, 'kind': 'text-hardcoded', 'hex': _to_hex(rgb),
                         'lr': contrast(rgb[:3], theme.light_canvas),
                         'dr': contrast(rendered_dark_text(rgb, f.has_adapter), theme.dark_canvas),
                         'fail': True})
    return rows


def fmt(x):
    return '{:>5.2f}:1'.format(x)


def report(rows, theme):
    out = []
    out.append('THEME SURFACES (github scheme)')
    out.append('  light canvas {}   dark canvas {}'.format(_to_hex(theme.light_canvas), _to_hex(theme.dark_canvas)))
    out.append('  theme text   light {} ({})  dark {} ({})'.format(
        _to_hex(theme.light_text), fmt(contrast(theme.light_text, theme.light_canvas)),
        _to_hex(theme.dark_text), fmt(contrast(theme.dark_text, theme.dark_canvas))))
    out.append('')

    series = [r for r in rows if r['kind'] == 'series' and not r['f'].accepted]
    accepted = [r for r in rows if r['f'].accepted]
    text_hard = [r for r in rows if r['kind'] == 'text-hardcoded']
    text_themed = [r for r in rows if r['kind'] == 'text-themed']

    if series:
        out.append('SERIES COLORS  (floor {:.0f}:1; both themes must pass; adapter-aware)'.format(MARK_FLOOR))
        out.append('  {:<9} {:<9} {:<7} {:<6} {:<22} {}'.format('LIGHT', 'DARK', 'STATUS', 'MARK', 'COLOR (dark render)', 'WHERE'))
        for r in sorted(series, key=lambda r: (0 if r['fail'] else 1, r['hex'])):
            f = r['f']
            dark_disp = r['hex'] if r['hex'] == r['dark_hex'] else '{} -> {}'.format(r['hex'], r['dark_hex'])
            loc = '{}:{} chart#{}{}'.format(os.path.relpath(f.file), f.line, f.chart_idx,
                                            ' (fill)' if f.role == 'series-fill' else '')
            out.append('  {:<9} {:<9} {:<7} {:<6} {:<22} {}'.format(
                fmt(r['lr']), fmt(r['dr']), 'FAIL' if r['fail'] else 'ok', f.mark, dark_disp.lower(), loc))
        out.append('')

    out.append('TEXT ELEMENTS  (title / axis / tick / legend / grid)')
    if text_themed:
        ex = text_themed[0]
        out.append('  theme-aware (window.__tc/__gc or Chart.defaults): {} slot(s), light {} / dark {}  ok'.format(
            len(text_themed), fmt(ex['lr']), fmt(ex['dr'])))
    if text_hard:
        out.append('  HARDCODED (BUG-034 violation; must be theme-driven):')
        for r in text_hard:
            f = r['f']
            out.append('    {:<10} {:<18} light {} dark {}  {}:{} chart#{}'.format(
                f.role, f.literal, fmt(r['lr']), fmt(r['dr']), os.path.relpath(f.file), f.line, f.chart_idx))
    if not text_themed and not text_hard:
        out.append('  none found in chart bodies (theme defaults in effect)')
    out.append('')

    if accepted:
        out.append('ACCEPTED (documented inline via audit-ok / audit-accept)')
        for r in accepted:
            f = r['f']
            out.append('    {:<22} {}:{} chart#{}'.format(str(r.get('hex', f.literal)).lower(),
                       os.path.relpath(f.file), f.line, f.chart_idx))
        out.append('')

    return '\n'.join(out)


# ----------------------------------------------------------------------------
# Fix
# ----------------------------------------------------------------------------

def plan_fixes(rows, theme, fix_all):
    edits, notes, unresolved = [], [], 0
    used, remap_cache = {}, {}
    for r in rows:
        if r['kind'] == 'series' and not r['fail'] and not r['f'].accepted:
            used.setdefault((r['f'].file, r['f'].chart_idx), set()).add(r['hex'])

    for r in rows:
        f = r['f']
        if r['kind'] == 'text-hardcoded':
            edits.append((f.start, f.end, f.strip_repl, 'strip {} {}'.format(f.role, f.literal)))
            continue
        if r['kind'] != 'series' or not r['fail'] or f.accepted:
            continue
        invisible = r['hex'] in ('#000000', '#FFFFFF') and not (
            f.has_adapter and r['hex'].upper() in DARK_SWAP)
        if not invisible and not fix_all:
            unresolved += 1
            continue
        if f.role == 'series-fill' and not invisible and not fix_all:
            unresolved += 1
            continue
        ck = (f.file, f.chart_idx, r['hex'])
        repl = remap_cache.get(ck)
        if repl is None:
            repl = best_replacement(r['hex'], theme, used.get((f.file, f.chart_idx), set()), f.has_adapter)
            if repl is None:
                unresolved += 1
                notes.append('NO SAFE REPLACEMENT for {} at {}:{} (decide manually per BUG-022)'.format(
                    r['hex'], os.path.relpath(f.file), f.line))
                continue
            remap_cache[ck] = repl
            used.setdefault((f.file, f.chart_idx), set()).add(repl)
        new_literal = f.literal.replace(r['hex'], repl).replace(r['hex'].lower(), repl)
        if new_literal == f.literal:
            pr = _parse_color(repl)
            new_literal = re.sub(r'rgba?\([^)]*\)', lambda m: _swap_rgba(m.group(0), pr), f.literal)
        edits.append((f.start, f.end, new_literal, 'remap {} -> {}'.format(r['hex'], repl)))
        notes.append('{}:{} chart#{}  {} -> {}'.format(os.path.relpath(f.file), f.line, f.chart_idx, r['hex'], repl))
    return edits, notes, unresolved


def _swap_rgba(literal, rgb):
    p = _parse_color(literal)
    a = p[3] if p else 1.0
    return ('rgb({}, {}, {})'.format(*rgb[:3]) if a >= 0.999
            else 'rgba({}, {}, {}, {:g})'.format(rgb[0], rgb[1], rgb[2], a))


def apply_edits(text, edits):
    for start, end, repl, _ in sorted(edits, key=lambda e: e[0], reverse=True):
        text = text[:start] + repl + text[end:]
    return text


# ----------------------------------------------------------------------------
# Driver
# ----------------------------------------------------------------------------

def iter_targets(paths):
    for p in paths:
        if os.path.isfile(p) and p.endswith('.md'):
            yield p
        elif os.path.isdir(p):
            for root, _, files in os.walk(p):
                for name in sorted(files):
                    if name.endswith('.md'):
                        yield os.path.join(root, name)


def self_test(theme):
    print(report([], theme))
    print('APPROVED PALETTE two-mode check (adapter swap applied where relevant):')
    print('  {:<9} {:<9} {:<9} {:<20} {}'.format('LIGHT', 'DARK', 'STATUS', 'COLOR', 'PASSES BOTH?'))
    for c in APPROVED:
        lr, dr, dhex = series_ratios(c, theme, has_adapter=True)
        disp = c if c == dhex else '{} -> {}'.format(c, dhex)
        ok = 'yes' if (lr >= MARK_FLOOR and dr >= MARK_FLOOR) else 'NO'
        print('  {:<9} {:<9} {:<9} {:<20} {}'.format(fmt(lr), fmt(dr), grade(min(lr, dr)), disp.lower(), ok))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='*', default=['content'])
    ap.add_argument('--fix', action='store_true')
    ap.add_argument('--fix-all', action='store_true')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--self-test', action='store_true')
    ap.add_argument('--scheme-css')
    ap.add_argument('--light-canvas')
    ap.add_argument('--dark-canvas')
    args = ap.parse_args(argv)

    neutral = load_scheme_css(args.scheme_css) if args.scheme_css else None
    lc = _parse_color(args.light_canvas)[:3] if args.light_canvas else None
    dc = _parse_color(args.dark_canvas)[:3] if args.dark_canvas else None
    theme = Theme(neutral_light=neutral, light_canvas=lc, dark_canvas=dc)

    if args.self_test:
        self_test(theme)
        return 0

    paths = args.paths if args.paths else ['content']
    targets = list(iter_targets(paths))
    if not targets:
        print('No markdown files found under: {}'.format(', '.join(paths)), file=sys.stderr)
        return 2

    all_rows, file_findings = [], {}
    for path in targets:
        text = open(path, encoding='utf-8').read()
        fs = scan_text(text, path)
        if fs:
            file_findings[path] = (text, fs)
            all_rows.extend(evaluate(fs, theme))

    if args.json:
        payload = [{'file': os.path.relpath(r['f'].file), 'line': r['f'].line, 'chart': r['f'].chart_idx,
                    'role': r['f'].role, 'mark': r['f'].mark, 'kind': r['kind'],
                    'literal': r['f'].literal, 'hex': r.get('hex'),
                    'light_ratio': round(r.get('lr', 0), 3), 'dark_ratio': round(r.get('dr', 0), 3),
                    'accepted': r['f'].accepted, 'fail': r.get('fail', False)} for r in all_rows]
        print(json.dumps(payload, indent=2))
        return 1 if any(p['fail'] and not p['accepted'] for p in payload) else 0

    if not args.fix and not args.fix_all:
        print(report(all_rows, theme))
        problems = [r for r in all_rows if r.get('fail') and not r['f'].accepted]
        print('{} color slot(s) across {} file(s); {} issue(s) flagged ({} accepted and excluded).'.format(
            len(all_rows), len(file_findings), len(problems),
            sum(1 for r in all_rows if r['f'].accepted)))
        if problems:
            print('Run with --fix for safe fixes, --fix-all to also remap FAIL series.')
        return 1 if problems else 0

    total_unresolved, changed = 0, []
    for path, (text, fs) in file_findings.items():
        rows = evaluate(fs, theme)
        edits, notes, unresolved = plan_fixes(rows, theme, args.fix_all)
        total_unresolved += unresolved
        if not edits:
            continue
        backup = '{}.backup-{}'.format(path, datetime.now().strftime('%Y%m%d-%H%M%S'))
        shutil.copy2(path, backup)
        open(path, 'w', encoding='utf-8').write(apply_edits(text, edits))
        changed.append((path, backup, notes))

    if not changed:
        print('No auto-fixable issues found.')
    for path, backup, notes in changed:
        print('fixed: {}  (backup: {})'.format(os.path.relpath(path), os.path.relpath(backup)))
        for n in notes:
            print('   {}'.format(n))

    post = []
    for path in [c[0] for c in changed] or targets:
        post.extend(evaluate(scan_text(open(path, encoding='utf-8').read(), path), theme))
    remaining = [r for r in post if r.get('fail') and not r['f'].accepted]
    print('\nRe-audit: {} issue(s) remaining.'.format(len(remaining)))
    for r in remaining:
        f = r['f']
        print('   {} {}:{} chart#{} {}'.format('FAIL' if r['kind'] == 'series' else 'hardcoded',
              os.path.relpath(f.file), f.line, f.chart_idx, r.get('hex') or f.literal))
    print('\nVerify:')
    print('  python3 tools/audit_figures.py        # expect: 0 issues flagged')
    return 1 if remaining else 0


if __name__ == '__main__':
    sys.exit(main())
