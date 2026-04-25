# Portfolio

Monospace-driven personal site. Dark by default, light when the visitor's system prefers light. Color-blind friendly throughout.

## Project structure

```
portfolio/
├── fonts/
│   ├── MonoLisaVariable.woff2
│   └── MonoLisaVariableItalic.woff2
├── index.html
├── styles.css
├── resume.pdf
└── README.md
```

## Setup

### 1. Add MonoLisa Variable

The Complete bundle ships several formats. You want the variable woff2 files from the web-fonts folder. Drop them into a `fonts/` folder in the project root.

The `@font-face` declarations expect:

```
fonts/MonoLisaVariable.woff2
fonts/MonoLisaVariableItalic.woff2
```

Faceless has used a few naming conventions over the years. If your bundle uses different names (`MonoLisa-Variable.woff2`, `MonoLisaVariableNormal.woff2`, etc.), either rename or update the `src` paths at the top of `styles.css`.

### 2. Customize content

Open `index.html` and replace anything marked `[Edit: ...]` or `[Date]` / `[Year]` with real values. Specifically:

- Hero tagline
- About paragraphs
- Project descriptions for `qualtrics-processing-pipeline`, `ai_csv_profiler`, and `qualtrics-report-generator`
- Experience dates and one-line summaries
- Education years
- Earlier Georgetown role title

### 3. Add resume PDF

Drop a `resume.pdf` into the project root. The hero already links to it.

### 4. Preview locally

Opening `index.html` directly works for layout, but browsers block local font loading on `file://`. Run a static server:

```
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

### 5. Deploy to GitHub Pages

Recommended: name the repo `hihipy.github.io` for a clean root URL.

```
git init
git add .
git commit -m "Initial portfolio"
git branch -M main
git remote add origin https://github.com/hihipy/hihipy.github.io.git
git push -u origin main
```

In repo Settings → Pages, set source to `main` branch, root folder. Site goes live at `hihipy.github.io` within a minute or two.

## Theming

Color tokens live at the top of `styles.css`:

- `:root` defines the dark palette (default)
- `@media (prefers-color-scheme: light)` overrides with the light palette

The accent is the only personality knob worth touching. Both modes use values from the Okabe-Ito palette, so any swap should stay within that set to preserve color-blind safety.

Dark accent options: `#FFB454` (amber, current), `#56B4E9` (sky blue), `#009E73` (bluish green).
Light accent options: `#0072B2` (deep blue), `#D55E00` (vermillion), `#BA7517` (deep amber, current).

## Signature detail

Project titles transition between weight 500 and weight 700 on hover, animated smoothly via `font-variation-settings`. This works because MonoLisa Variable is a true variable font, with every weight in the 100-800 range interpolated from a single file. A static font cannot do this.

## MonoLisa features enabled

The body declaration enables three OpenType features by default:

- `calt` for contextual alternates (coding ligatures: `=>`, `==`, `!=`, `<=`, `>=`)
- `liga` for standard ligatures
- `zero` for slashed zero, distinguishes 0 from O at small sizes

MonoLisa also ships ~18 stylistic sets for alternate character forms (single-story `a`, single-story `g`, serif-bottom `i`, alternate `r`, etc.). Common picks are noted in a comment block at the top of `styles.css`. To try one, add it to the `font-feature-settings` line on body. The stylistic sets PDF in your bundle has visual examples of each.

## License notes

You're on MonoLisa Complete, which permits web embedding. The `@font-face` declarations only ship the woff2 files to visitors' browsers (no exposed download links), which aligns with Faceless's standard usage terms. Keep the source font files out of any public asset listing if you fork or hand off the repo.

The portfolio code itself (HTML, CSS) is yours to do with as you wish.
