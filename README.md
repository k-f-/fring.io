## Personal Website

What it says on the tin. 😉

**Live at**: https://fring.io

## Current Live Version

**🟢 v3** (defined in `VERSION` file)

To change the live version, update:
1. `VERSION` file in repo root
2. `LATEST_VERSION` in `.github/workflows/deploy.yml`
3. This README

## Structure

This is a monorepo containing all versions of the site:

```
sites/
  ├── v1/  # Jekyll blog (2013-2015)
  ├── v2/  # Minimal HTML (2015-2020)
  └── v3/  # Refined minimal (2020-present) ← LIVE

infrastructure/
  ├── provision-site.sh
  └── iam-policy-local-dev.json

.github/workflows/
  └── deploy.yml
```

## Content Management

**Version-agnostic content** lives in `content/` and is managed via markdown-first workflow:

```
content/
  ├── books.json      # Canonical data (generated from .md)
  ├── books.md        # Human-editable source
  ├── career.json     # Canonical data (generated from .md)
  ├── career.md       # Human-editable source
  ├── now.json        # Canonical data (generated from .md)
  ├── now.md          # Human-editable source
  ├── albums.json     # Canonical data (generated from .md)
  └── albums.md       # Human-editable source

infrastructure/
  ├── json_to_markdown.py   # JSON → MD export (all files)
  ├── parse_books.py        # MD → JSON parser (books)
  ├── parse_career.py       # MD → JSON parser (career)
  ├── parse_now.py          # MD → JSON parser (now)
  ├── parse_albums.py       # MD → JSON parser (albums)
  └── migrate_albums.py     # One-time migration script
```

### Workflow: Editing Content

**Edit markdown files directly** (preferred human workflow):
```bash
# Edit any content file
vim content/albums.md
vim content/books.md
vim content/career.md
vim content/now.md

# Parse markdown back to JSON
python3 infrastructure/parse_albums.py
python3 infrastructure/parse_books.py
python3 infrastructure/parse_career.py
python3 infrastructure/parse_now.py

# Commit both .md and .json files
git add content/
git commit -m "Update content"
```

**Export JSON to markdown** (for initial setup or bulk changes):
```bash
# Export all JSON files to markdown
python3 infrastructure/json_to_markdown.py --file all

# Export single file
python3 infrastructure/json_to_markdown.py --file albums

# Preview without writing
python3 infrastructure/json_to_markdown.py --file albums --preview
```

**Round-trip conversion** (lossless for all files):
```bash
# JSON → MD → JSON preserves all data
python3 infrastructure/json_to_markdown.py --file all
python3 infrastructure/parse_books.py
python3 infrastructure/parse_career.py
python3 infrastructure/parse_now.py
python3 infrastructure/parse_albums.py
# Result: Identical JSON (except timestamps)
```

### Markdown Format

Albums use `[YYYY-MM-DD]` prefix for exact date preservation:
```markdown
### [2019-10-21] The Jackson 5 - Gold
**Released:** 2005
**Listen:** [Spotify](https://open.spotify.com/album/...)
**Duration:** 36 tracks, 2 hr 13 min.

hits. that Motown sound.
```

## Development

**To work on v3 (current):**
```bash
cd sites/v3/
# Edit index.html, CSS, etc.
git add sites/v3/
git commit -m "Update v3 design"
git push origin main
# Deploys to both s3://v3.fring.io and s3://fring.io (apex)
```

**To create v4 (future version):**
```bash
# 1. Provision AWS infrastructure
./infrastructure/provision-site.sh v4

# 2. Create v4 directory
mkdir sites/v4
cp sites/v3/* sites/v4/  # Start from v3

# 3. Work on v4
cd sites/v4/
# Edit files as needed

# 4. Commit and push (will deploy to v4.fring.io only)
git add sites/v4/
git commit -m "Add v4 site"
git push origin main
```

**To launch v4 (make it live):**

See LAUNCH_CHECKLIST.md for complete procedure. Summary:
1. Update VERSION file → `echo "v4" > VERSION`
2. Update LATEST_VERSION in .github/workflows/deploy.yml
3. Update README.md "Current Live Version" section
4. Commit and push

## Deployment

**Automatic:** Push to `main` branch with changes in `sites/` triggers deployment.

**Manual:** Use GitHub Actions workflow dispatch to deploy any version.

### How it works

All version sites are independently accessible at their versioned URLs. When you update any version:
1. **Versioned bucket** always deploys (e.g., s3://v3.fring.io)
2. **Apex bucket** also deploys if it's the LATEST_VERSION (s3://fring.io, s3://kfring.com)

The `LATEST_VERSION` in `.github/workflows/deploy.yml` controls which version appears at the apex domains (fring.io, kfring.com). All other versions remain accessible at their versioned URLs.

**Live URLs:**
- https://fring.io, https://www.fring.io → Latest version (v3)
- https://kfring.com, https://www.kfring.com → Latest version (v3)
- https://v3.fring.io, https://v3.kfring.com → v3 (current latest)
- https://v2.fring.io, https://v2.kfring.com → v2 (previous version)
- https://v1.fring.io, https://v1.kfring.com → v1 (original)

See [DEPLOYMENT_ARCHITECTURE.md](DEPLOYMENT_ARCHITECTURE.md) for complete details.
