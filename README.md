# pgbd.casa

Personal site of Philip Bachas-Daunert. Built with Hugo and the Blowfish theme.

## What's in this scaffold

Everything you need to run the site is already here, except the Blowfish theme itself, which is added as a git submodule (one command, see below).

```
pgbd-casa/
├── .github/workflows/hugo.yml    GitHub Pages deployment
├── .gitignore                    Hugo build artifacts excluded from git
├── README.md                     this file
├── config/_default/
│   ├── hugo.toml                 site config (baseURL, etc.)
│   ├── languages.en.toml         site title, author info
│   ├── menus.en.toml             nav menu (~/sala, ~/cv)
│   ├── markup.toml               Hugo markup config (required)
│   └── params.toml               Blowfish theme parameters
├── assets/css/custom.css         MonoLisa font override
├── content/
│   ├── _index.md                 home page
│   ├── sala/_index.md            about page placeholder
│   └── cv/_index.md              resume page
└── static/
    ├── CNAME                     custom domain (pgbd.casa)
    ├── resume.pdf                your resume PDF
    └── fonts/
        ├── MonoLisaVariable.woff2
        └── MonoLisaVariableItalic.woff2
```

## Setup

You should already have:
- Hugo installed (`brew install hugo` if not)
- Git installed
- An empty `hihipy.github.io` repo with the old casa archived to a separate branch

### 1. Drop the scaffold contents into your repo

```bash
cd "/Users/philipbachas-daunert/Library/CloudStorage/ProtonDrive-philgbd@pm.me-folder/Code/coding-workspace/hihipy.github.io"

# extract the tarball into the current directory
# the --strip-components=1 flag unwraps the outer folder
tar -xzf ~/Downloads/pgbd-casa-scaffold.tar.gz --strip-components=1

# verify the files landed correctly
ls -la
# you should see config/ content/ assets/ static/ .github/ README.md .gitignore
```

### 2. Add the Blowfish theme as a submodule

This is how Hugo themes work — you add the theme repo as a "submodule" pointer inside your repo, and git tracks the version. You don't download Blowfish separately; this command pulls it in:

```bash
git submodule add -b main https://github.com/nunocoracao/blowfish.git themes/blowfish
```

You'll see Blowfish's files appear under `themes/blowfish/`. The submodule is what actually styles the site.

### 3. Test locally

```bash
hugo server
```

Open `http://localhost:1313/` in your browser. You should see:
- "bienvenido a mi casa" as the homepage
- MonoLisa Variable as the font
- A theme toggle (sun/moon icon) in the header
- GitHub-style blue/gray color scheme

If it works, move to step 4.

### 4. Configure GitHub Pages

In your repo settings on GitHub:
1. Go to **Settings → Pages**
2. Under "Build and deployment", set **Source** to **GitHub Actions** (not "Deploy from a branch")

This tells GitHub to use the workflow at `.github/workflows/hugo.yml` to build and deploy the site.

### 5. Push

```bash
git add .
git commit -m "Migrate to Hugo + Blowfish"
git push
```

Watch the Actions tab on GitHub. The workflow takes about 1-2 minutes. Once green, the site is live at `pgbd.casa`.

## Adding a new project later

Each project is a markdown file. To add `25live-cleaner` to the `~/cocina` room:

```bash
mkdir -p content/cocina
# create content/cocina/_index.md (room hub page)
# create content/cocina/25live-cleaner.md (project deep page)
```

Project markdown files use frontmatter at the top:

```yaml
---
title: "25live-cleaner"
description: "Python utility that cleans 25Live exports"
date: 2025-08-01
tags: ["Python", "pandas", "ETL"]
---

# Content goes here in markdown
```

Push and the Action redeploys.

## Updating the Blowfish theme later

```bash
cd themes/blowfish
git pull origin main
cd ../..
git add themes/blowfish
git commit -m "Update Blowfish theme"
git push
```

## Troubleshooting

**Site looks unstyled.** Blowfish submodule probably wasn't added correctly. Run `ls themes/blowfish/` — if empty, run `git submodule update --init --recursive`.

**Font is wrong.** Check that the woff2 files are at `static/fonts/MonoLisaVariable.woff2` and `static/fonts/MonoLisaVariableItalic.woff2`. The browser DevTools Network tab will show 404s if the path is wrong.

**Build fails on GitHub.** Open the failed workflow run in the Actions tab and read the log. Common causes: missing submodule, invalid TOML syntax, Hugo version mismatch.
