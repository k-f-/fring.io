## Personal Website

What it says on the tin. 😉

**Live at**: https://fring.io

## Structure

This is a monorepo containing all versions of the site:

```
sites/
  ├── v1/  # Jekyll blog (2013-2015)
  ├── v2/  # Minimal HTML (2015-2020)
  ├── v3/  # Refined minimal (2020-2024)
  └── v4/  # Current version (2024-present)

infrastructure/
  ├── provision-site.sh
  └── iam-policy-local-dev.json

.github/workflows/
  └── deploy.yml
```

## Development

**To work on v4 (latest):**
```bash
cd sites/v4/
# Edit index.html, CSS, etc.
git add sites/v4/
git commit -m "Update v4 design"
git push origin main
```

**To create v5:**
```bash
# 1. Provision AWS infrastructure
./infrastructure/provision-site.sh v5

# 2. Create v5 directory
mkdir sites/v5
cp sites/v4/* sites/v5/  # Start from v4

# 3. Update LATEST_VERSION in .github/workflows/deploy.yml
# Change: LATEST_VERSION: v4
# To:     LATEST_VERSION: v5

# 4. Commit and push
git add sites/v5/ .github/workflows/deploy.yml
git commit -m "Add v5 site"
git push origin main
```

## Deployment

**Automatic:** Push to `main` branch with changes in `sites/` triggers deployment.

**Manual:** Use GitHub Actions workflow dispatch to deploy any version.

When you update a version:
1. **Versioned bucket** deploys (e.g., s3://v4.fring.io)
2. **Main bucket** also deploys if it's the latest version (s3://fring.io)

**URLs:**
- https://fring.io, https://www.fring.io → Latest version (v4)
- https://kfring.com, https://www.kfring.com → Latest version (v4)
- https://v4.fring.io → v4 specifically
- https://v3.kfring.com → v3 specifically
- https://v2.fring.io, https://v2.kfring.com → v2
- https://v1.fring.io, https://v1.kfring.com → v1

See [DEPLOYMENT_ARCHITECTURE.md](DEPLOYMENT_ARCHITECTURE.md) for complete details.
