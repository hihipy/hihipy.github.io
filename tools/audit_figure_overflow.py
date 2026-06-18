#!/usr/bin/env python3
"""
audit_figure_overflow.py

Render each page of the site in headless chromium at a mobile width and a
desktop width, then measure the real layout boxes to find what breaks
responsive layout. Desktop usually behaves; mobile is where things overflow,
so both widths are checked and compared.

Three things are checked per page, per width:

1. Page overflow. Does the document get a horizontal scrollbar? Measured as
   scrollWidth minus clientWidth. This is the ground truth for the bug.

2. Figure containment. For every figure-like element that exceeds the width,
   is the overflow handled or not?
     scroll  inside an overflow-x auto or scroll box that fits the width.
             Scrollable in place, the way code blocks and KaTeX behave. ok.
     clip    inside an overflow-x hidden box. Content cut off. warn.
     none    reaches the document. The page scrolls horizontally. problem.

3. Cause attribution. When the page overflows, name the element that sets the
   width. Scroll-contained elements (code blocks, scrollable math) are excluded
   so they stop masking the real offender. If nothing uncontained is found, the
   widest elements are listed with their containment marked, so there is always
   something to look at.

4. Chart rendering. Every canvas (Chart.js renders to canvas) is checked for
   collapse (zero height), blank output (nothing drawn), and overflow, and the
   mobile result is compared against desktop. A chart that draws on desktop but
   collapses, goes blank, or overflows on mobile is the regression to catch.

Exit status: 0 clean, 1 problems found, 2 setup or run error.

Usage
  python3 tools/audit_figure_overflow.py
  python3 tools/audit_figure_overflow.py --paths /cocina/25live-cleaner/
  python3 tools/audit_figure_overflow.py --mobile-width 360 --json figure_audit.json
  python3 tools/audit_figure_overflow.py --strict   # clipped figures also fail

Requires
  pip install playwright --break-system-packages
  python3 -m playwright install chromium
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from urllib.parse import urlparse, urlunparse
from xml.etree import ElementTree

from playwright.sync_api import sync_playwright, Error as PlaywrightError


# Figure-like elements: anything that can carry intrinsic width and break out of
# the text column. pre is included so the report can show code blocks landing in
# the scroll bucket, confirming the contrast with figures that do not.
FIGURE_SELECTOR = (
    "img, svg, canvas, table, figure, iframe, video, pre, "
    ".mermaid, [class*='chart'], [class*='Chart']"
)

DEFAULT_TOLERANCE = 2


# Shared JS: a containment classifier reused by every probe so the definition of
# "handled overflow" is identical across figure, cause, and chart checks.
JS_HELPERS = r"""
const TOL = __TOL__;
const cw = document.documentElement.clientWidth;
function containment(el) {
  let n = el.parentElement;
  while (n && n !== document.documentElement) {
    const ox = getComputedStyle(n).overflowX;
    if (ox === 'auto' || ox === 'scroll' || ox === 'hidden' || ox === 'clip') {
      const r = n.getBoundingClientRect();
      if (r.right <= cw + TOL && r.left >= -TOL) {
        return (ox === 'hidden' || ox === 'clip') ? 'clip' : 'scroll';
      }
    }
    n = n.parentElement;
  }
  return 'none';
}
function classOf(el) {
  let c = (typeof el.className === 'string') ? el.className : (el.getAttribute('class') || '');
  return c.trim();
}
function visible(el) {
  const cs = getComputedStyle(el);
  if (cs.display === 'none' || cs.visibility === 'hidden') return false;
  if (cs.position === 'fixed') return false;
  const r = el.getBoundingClientRect();
  if (r.width === 0 && r.height === 0) return false;
  return true;
}
"""


MEASURE_JS = JS_HELPERS + r"""
return (() => {
  const vw = window.innerWidth;
  const sw = document.documentElement.scrollWidth;

  const offenders = [];
  for (const el of document.querySelectorAll(__SEL__)) {
    if (!visible(el)) continue;
    const r = el.getBoundingClientRect();
    if (!(r.right > cw + TOL || r.left < -TOL || r.width > cw + TOL)) continue;
    offenders.push({
      tag: el.tagName.toLowerCase(), cls: classOf(el), id: el.id || '',
      width: Math.round(r.width), left: Math.round(r.left), right: Math.round(r.right),
      overflow_px: Math.round(Math.max(r.right - cw, -r.left, r.width - cw)),
      contained: containment(el),
      snippet: (el.outerHTML || '').replace(/\s+/g, ' ').slice(0, 140),
    });
  }
  offenders.sort((a, b) => b.overflow_px - a.overflow_px);

  return {
    vw, client_width: cw, scroll_width: sw,
    overshoot: Math.max(0, sw - cw),
    has_page_overflow: sw > cw + TOL,
    offenders,
  };
})();
"""


# Cause attribution. Run only when the page overflows. Excludes scroll-contained
# elements so code blocks stop crowding out the real offender, collapses
# parent/child chains that share an edge, and falls back to the widest elements
# (marked with their containment) when nothing uncontained is found.
CAUSE_JS = JS_HELPERS + r"""
return (() => {
  const all = [];
  for (const el of document.querySelectorAll('body *')) {
    if (!visible(el)) continue;
    const r = el.getBoundingClientRect();
    if (r.right <= cw + TOL) continue;
    const p = el.parentElement;
    const pr = p ? p.getBoundingClientRect() : null;
    const cs = getComputedStyle(el);
    all.push({
      el,
      tag: el.tagName.toLowerCase(), cls: classOf(el), id: el.id || '',
      width: Math.round(r.width), right: Math.round(r.right),
      overflow_px: Math.round(r.right - cw),
      contained: containment(el),
      parent_fits: !pr || pr.right <= cw + TOL,
      css_width: cs.width, css_min_width: cs.minWidth, position: cs.position,
      margin_left: cs.marginLeft, margin_right: cs.marginRight,
      snippet: (el.outerHTML || '').replace(/\s+/g, ' ').slice(0, 160),
    });
  }

  // Collapse parent/child chains that share the same right edge: keep the
  // outermost (the one whose parent does not also overflow).
  const strip = (o) => { const {el, ...rest} = o; return rest; };

  // Prime causes: uncontained elements that introduce the width relative to a
  // parent that fits. These are the real offenders.
  let causes = all.filter(o => o.contained === 'none' && o.parent_fits);
  causes.sort((a, b) => b.right - a.right);

  if (causes.length === 0) {
    // Nothing uncontained introduces it. Surface the widest elements, marked
    // with containment, so the real extent is visible even if handled. Dedupe
    // by (right, width) to collapse code-span chains.
    const seen = new Set();
    const widest = [];
    all.sort((a, b) => b.right - a.right);
    for (const o of all) {
      const key = o.right + ':' + o.width + ':' + o.tag;
      if (seen.has(key)) continue;
      seen.add(key);
      widest.push(o);
    }
    return { kind: 'widest', items: widest.slice(0, 12).map(strip) };
  }
  return { kind: 'cause', items: causes.slice(0, 12).map(strip) };
})();
"""


# Chart rendering. Every canvas, with whether it drew anything, whether it
# collapsed, and whether it overflows the width.
CHART_JS = JS_HELPERS + r"""
return (() => {
  const out = [];
  const canvases = document.querySelectorAll('canvas');
  let idx = 0;
  for (const el of canvases) {
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    const shown = !(cs.display === 'none' || cs.visibility === 'hidden');
    let blank = null; // null = could not sample
    try {
      const ctx = el.getContext('2d');
      if (ctx && el.width > 0 && el.height > 0) {
        // Sample a grid rather than the whole bitmap, for speed.
        const w = el.width, h = el.height;
        const data = ctx.getImageData(0, 0, w, h).data;
        let painted = false;
        const step = Math.max(1, Math.floor((w * h) / 4000)) * 4;
        for (let i = 3; i < data.length; i += step) {
          if (data[i] !== 0) { painted = true; break; }
        }
        blank = !painted;
      }
    } catch (e) { blank = null; }
    out.push({
      index: idx++,
      cls: classOf(el), id: el.id || '',
      css_width: Math.round(r.width), css_height: Math.round(r.height),
      bitmap_width: el.width, bitmap_height: el.height,
      right: Math.round(r.right),
      shown,
      collapsed: shown && r.height < 10,
      blank,
      overflows: r.right > cw + TOL || r.width > cw + TOL,
      contained: containment(el),
    });
  }
  return out;
})();
"""


def build(js: str, tol: int, sel: str | None = None) -> str:
    js = js.replace("__TOL__", str(tol))
    if sel is not None:
        js = js.replace("__SEL__", json.dumps(sel))
    return "() => {\n" + js + "\n}"


@dataclass
class ViewportResult:
    label: str
    width: int
    vw: int = 0
    client_width: int = 0
    scroll_width: int = 0
    overshoot: int = 0
    has_page_overflow: bool = False
    offenders: list = field(default_factory=list)
    cause_kind: str = ""
    causes: list = field(default_factory=list)
    charts: list = field(default_factory=list)
    error: str = ""

    @property
    def problems(self) -> list:
        return [o for o in self.offenders if o["contained"] == "none"]

    @property
    def warns(self) -> list:
        return [o for o in self.offenders if o["contained"] == "clip"]

    @property
    def ok(self) -> list:
        return [o for o in self.offenders if o["contained"] == "scroll"]

    @property
    def chart_problems(self) -> list:
        return [c for c in self.charts if c["collapsed"] or c["overflows"]]

    @property
    def chart_blanks(self) -> list:
        return [c for c in self.charts if c["blank"] is True]

    @property
    def chart_unknowns(self) -> list:
        # Canvases that could not be pixel-sampled (e.g. tainted). Their draw
        # state is unverified, so a "0 blank" result is only meaningful net of
        # these.
        return [c for c in self.charts if c["blank"] is None]

    @property
    def flagged(self) -> bool:
        return bool(self.error or self.has_page_overflow or self.problems
                    or self.warns or self.chart_problems)

    def failing(self, strict: bool) -> bool:
        hard = bool(self.error or self.has_page_overflow or self.problems
                    or self.chart_problems)
        return hard or (strict and bool(self.warns))


@dataclass
class PageResult:
    path: str
    viewports: list = field(default_factory=list)

    @property
    def flagged(self) -> bool:
        return any(v.flagged for v in self.viewports) or bool(self.chart_regressions)

    def failing(self, strict: bool) -> bool:
        return any(v.failing(strict) for v in self.viewports) or bool(self.chart_regressions)

    @property
    def _by_label(self) -> dict:
        return {v.label: v for v in self.viewports}

    @property
    def chart_regressions(self) -> list:
        # Charts that render on desktop but break on mobile.
        d = self._by_label.get("desktop")
        m = self._by_label.get("mobile")
        if not d or not m:
            return []
        d_by_i = {c["index"]: c for c in d.charts}
        out = []
        for c in m.charts:
            dc = d_by_i.get(c["index"])
            if not dc:
                continue
            desktop_ok = (not dc["collapsed"] and not dc["overflows"]
                          and dc["blank"] is not True)
            if not desktop_ok:
                continue
            reasons = []
            if c["collapsed"]:
                reasons.append("collapsed")
            if c["overflows"]:
                reasons.append("overflows")
            if c["blank"] is True:
                reasons.append("blank")
            if reasons:
                out.append({"index": c["index"], "cls": c["cls"], "id": c["id"],
                            "reasons": reasons,
                            "mobile": c, "desktop": dc})
        return out


def discover_paths(context, base_url: str) -> list:
    sitemap_url = base_url.rstrip("/") + "/sitemap.xml"
    try:
        resp = context.request.get(sitemap_url, timeout=15000)
        if not resp.ok:
            return []
        body = resp.text()
    except PlaywrightError:
        return []
    try:
        root = ElementTree.fromstring(body)
    except ElementTree.ParseError:
        return []
    paths, seen = [], set()
    for loc in root.iter():
        if loc.tag.endswith("loc") and loc.text:
            p = urlparse(loc.text.strip()).path or "/"
            if p not in seen:
                seen.add(p)
                paths.append(p)
    return paths


def rebase(base_url: str, path: str) -> str:
    base = urlparse(base_url)
    if path.startswith("http://") or path.startswith("https://"):
        path = urlparse(path).path or "/"
    if not path.startswith("/"):
        path = "/" + path
    return urlunparse((base.scheme, base.netloc, path, "", "", ""))


def measure_page(context, url, label, width, tol, settle_ms,
                 screenshots_dir=None, slug="") -> ViewportResult:
    result = ViewportResult(label=label, width=width)
    page = context.new_page()
    try:
        page.goto(url, wait_until="networkidle", timeout=30000)
        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except PlaywrightError:
            pass
        page.wait_for_timeout(settle_ms)

        data = page.evaluate(build(MEASURE_JS, tol, FIGURE_SELECTOR))
        result.vw = data["vw"]
        result.client_width = data["client_width"]
        result.scroll_width = data["scroll_width"]
        result.overshoot = data["overshoot"]
        result.has_page_overflow = data["has_page_overflow"]
        result.offenders = data["offenders"]

        result.charts = page.evaluate(build(CHART_JS, tol))

        if screenshots_dir and result.charts:
            import os
            handles = page.query_selector_all("canvas")
            for i, h in enumerate(handles):
                try:
                    # Scroll it into view so virtualized or lazy canvases paint.
                    h.scroll_into_view_if_needed(timeout=3000)
                    page.wait_for_timeout(250)
                    fn = "{0}__{1}__canvas{2}.png".format(slug, label, i)
                    h.screenshot(path=os.path.join(screenshots_dir, fn))
                except PlaywrightError:
                    pass

        problems = [o for o in result.offenders if o["contained"] == "none"]
        if result.has_page_overflow and not problems:
            cause = page.evaluate(build(CAUSE_JS, tol))
            result.cause_kind = cause["kind"]
            result.causes = cause["items"]
    except PlaywrightError as exc:
        result.error = str(exc).splitlines()[0]
    finally:
        page.close()
    return result


def describe(o) -> str:
    label = o["tag"] if "tag" in o else "canvas"
    if o.get("id"):
        label += "#" + o["id"]
    if o.get("cls"):
        label += "." + o["cls"].split()[0]
    return label


def print_report(pages, mobile_w, desktop_w, base_url, show_charts=False) -> None:
    print()
    print("Figure and chart audit  " + base_url)
    print("Mobile {0}px / Desktop {1}px".format(mobile_w, desktop_w))
    print("=" * 64)

    attention = mobile_of = desktop_of = chart_regr = 0
    total_charts = pages_with_charts = chart_issue = chart_blank = chart_unknown = 0

    for pr in pages:
        print()
        print(pr.path or "/")
        for v in pr.viewports:
            if v.error:
                print("  {0:<8} ERROR  {1}".format(v.label, v.error))
                continue
            if not v.flagged:
                print("  {0:<8} ok".format(v.label))
                continue

            if v.has_page_overflow:
                tag = "PAGE OVERFLOW"
                detail = "  scrollWidth {0} > clientWidth {1} (+{2})".format(
                    v.scroll_width, v.client_width, v.overshoot)
                if v.label == "mobile":
                    mobile_of += 1
                else:
                    desktop_of += 1
            elif v.problems:
                tag, detail = "FIGURE OVERFLOW", ""
            elif v.chart_problems:
                tag, detail = "CHART ISSUE", ""
            else:
                tag, detail = "FIGURE CLIPPED", ""
            print("  {0:<8} {1}{2}".format(v.label, tag, detail))

            for o in v.problems:
                print("    [problem] {0:<26} width {1}  right {2}  +{3} past edge  not contained".format(
                    describe(o), o["width"], o["right"], o["overflow_px"]))

            if v.has_page_overflow and not v.problems and v.causes:
                if v.cause_kind == "cause":
                    print("    overflow not from a figure. element setting the width:")
                    for o in v.causes:
                        print("    [cause]   {0:<26} width {1}  right {2}  +{3}  css-width {4}  pos {5}".format(
                            describe(o), o["width"], o["right"], o["overflow_px"],
                            o["css_width"], o["position"]))
                else:
                    print("    no uncontained cause found. widest elements (containment marked):")
                    for o in v.causes:
                        print("    [{0:<7}] {1:<26} width {2}  right {3}  css-width {4}".format(
                            o["contained"], describe(o), o["width"], o["right"], o["css_width"]))

            for o in v.chart_problems:
                kinds = []
                if o["collapsed"]:
                    kinds.append("collapsed h={0}".format(o["css_height"]))
                if o["overflows"]:
                    kinds.append("overflows right={0}".format(o["right"]))
                print("    [chart]   canvas#{0} {1}  {2}".format(
                    o["index"], describe(o), ", ".join(kinds)))

            for o in v.warns:
                print("    [clipped] {0:<26} width {1}  cut off by overflow-x hidden ancestor".format(
                    describe(o), o["width"]))
            for o in v.ok:
                print("    [ok]      {0:<26} width {1}  scrollable in place".format(
                    describe(o), o["width"]))

        for reg in pr.chart_regressions:
            chart_regr += 1
            print("  compare  CHART REGRESSION  canvas#{0} {1}  ok on desktop, {2} on mobile".format(
                reg["index"], describe(reg), " and ".join(reg["reasons"])))

        # Chart inventory: count canvases from whichever viewport saw the most,
        # and optionally print each one's mobile-vs-desktop rendered size.
        by_label = {v.label: v for v in pr.viewports}
        dv = by_label.get("desktop")
        mv = by_label.get("mobile")
        n_canvas = max(len(dv.charts) if dv else 0, len(mv.charts) if mv else 0)
        if n_canvas:
            pages_with_charts += 1
            total_charts += n_canvas
            for v in pr.viewports:
                chart_issue += len(v.chart_problems)
                chart_blank += len(v.chart_blanks)
                chart_unknown += len(v.chart_unknowns)
            if show_charts:
                d_by_i = {c["index"]: c for c in (dv.charts if dv else [])}
                m_by_i = {c["index"]: c for c in (mv.charts if mv else [])}
                for i in sorted(set(d_by_i) | set(m_by_i)):
                    d, m = d_by_i.get(i), m_by_i.get(i)
                    name = describe(d or m)
                    msz = "{0}x{1}".format(m["css_width"], m["css_height"]) if m else "-"
                    dsz = "{0}x{1}".format(d["css_width"], d["css_height"]) if d else "-"
                    drew = m or d
                    state = "blank" if drew and drew["blank"] is True else (
                        "unknown" if drew and drew["blank"] is None else "drawn")
                    def ar(c):
                        return round(c["css_width"] / c["css_height"], 2) if c and c["css_height"] else 0
                    print("    canvas#{0} {1:<22} mobile {2:<10} desktop {3:<10} ar m{4}/d{5} {6}".format(
                        i, name, msz, dsz, ar(m), ar(d), state))

        for v in pr.viewports:
            for b in v.chart_blanks:
                print("  {0:<8} note  canvas#{1} drew nothing (could be load timing; raise --settle-ms)".format(
                    v.label, b["index"]))

        if pr.flagged:
            attention += 1

    print()
    print("-" * 64)
    print("Pages checked: {0}".format(len(pages)))
    print("Pages with mobile page-overflow:  {0}".format(mobile_of))
    print("Pages with desktop page-overflow: {0}".format(desktop_of))
    print("Charts found: {0} across {1} page(s)".format(total_charts, pages_with_charts))
    print("Chart issues (collapse/overflow): {0}".format(chart_issue))
    print("Chart regressions desktop to mobile: {0}".format(chart_regr))
    print("Charts blank (check load timing): {0}".format(chart_blank))
    print("Charts not pixel-sampled (draw state unverified): {0}".format(chart_unknown))
    print("Pages needing attention:          {0}".format(attention))


def main() -> int:
    ap = argparse.ArgumentParser(description="Check figures and charts for responsive overflow and rendering at mobile and desktop widths.")
    ap.add_argument("--base-url", default="http://localhost:1313")
    ap.add_argument("--paths", nargs="*", default=None)
    ap.add_argument("--mobile-width", type=int, default=390)
    ap.add_argument("--desktop-width", type=int, default=1440)
    ap.add_argument("--tolerance", type=int, default=DEFAULT_TOLERANCE)
    ap.add_argument("--settle-ms", type=int, default=800,
                    help="Pause after load for Chart.js and Mermaid to draw.")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--strict", action="store_true",
                    help="Also fail on clipped figures.")
    ap.add_argument("--show-charts", action="store_true",
                    help="List every canvas with its mobile and desktop rendered size, even when healthy.")
    ap.add_argument("--screenshots", default=None, metavar="DIR",
                    help="Save a PNG of each canvas at both widths into DIR, so charts can be checked by eye.")
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    base_url = args.base_url.rstrip("/")
    pages = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--hide-scrollbars"])

            disco = browser.new_context()
            if args.paths:
                paths = args.paths
            else:
                paths = discover_paths(disco, base_url)
                if not paths:
                    print("Could not read {0}/sitemap.xml. Pass --paths, or check the server is up.".format(base_url),
                          file=sys.stderr)
                    disco.close(); browser.close(); return 2
            disco.close()
            if args.limit:
                paths = paths[: args.limit]

            shots = args.screenshots
            if shots:
                import os
                os.makedirs(shots, exist_ok=True)

            def slugify(rel):
                s = rel.strip("/").replace("/", "_")
                return s or "home"

            mobile_ctx = browser.new_context(
                viewport={"width": args.mobile_width, "height": 844},
                has_touch=True,
                user_agent=("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                            "Version/17.0 Mobile/15E148 Safari/604.1"),
            )
            desktop_ctx = browser.new_context(
                viewport={"width": args.desktop_width, "height": 900})

            for i, path in enumerate(paths, 1):
                url = rebase(base_url, path)
                rel = urlparse(url).path or "/"
                print("[{0}/{1}] {2}".format(i, len(paths), rel), file=sys.stderr)
                pr = PageResult(path=rel)
                slug = slugify(rel)
                pr.viewports.append(measure_page(mobile_ctx, url, "mobile", args.mobile_width, args.tolerance, args.settle_ms, shots, slug))
                pr.viewports.append(measure_page(desktop_ctx, url, "desktop", args.desktop_width, args.tolerance, args.settle_ms, shots, slug))
                pages.append(pr)

            mobile_ctx.close(); desktop_ctx.close(); browser.close()
    except PlaywrightError as exc:
        print("Browser error: {0}".format(exc), file=sys.stderr)
        print("If chromium is missing run: python3 -m playwright install chromium", file=sys.stderr)
        return 2

    print_report(pages, args.mobile_width, args.desktop_width, base_url, args.show_charts)

    if args.json:
        payload = [{"path": pr.path, "viewports": [asdict(v) for v in pr.viewports],
                    "chart_regressions": pr.chart_regressions} for pr in pages]
        with open(args.json, "w") as fh:
            json.dump(payload, fh, indent=2)
        print("\nWrote {0}".format(args.json))

    return 1 if any(pr.failing(args.strict) for pr in pages) else 0


if __name__ == "__main__":
    sys.exit(main())
