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
