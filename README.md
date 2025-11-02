## Personal Website

What it says on the tin. 😉

**Live at**: https://fring.io

## Structure

This is a monorepo containing all versions of the site:

```
sites/
  ├── v1/  # Jekyll blog (2013-2015)
  ├── v2/  # Minimal HTML (2015-2020)
  ├── v3/  # Refined minimal (2020-2024) ← LIVE
  └── v4/  # In development (2024-present)

infrastructure/
  ├── provision-site.sh
  └── iam-policy-local-dev.json

.github/workflows/
  └── deploy.yml
```

## Development

**To work on v4 (in development):**
```bash
cd sites/v4/
# Edit index.html, CSS, etc.
git add sites/v4/
git commit -m "Update v4 design"
git push origin main
# Note: Won't deploy to apex domains until LATEST_VERSION is changed to v4
```

**To launch v4 (make it live):**
```bash
# 1. Update workflow to make v4 live
sed -i '' 's/LATEST_VERSION: v3/LATEST_VERSION: v4/' .github/workflows/deploy.yml

# 2. Commit and push
git add .github/workflows/deploy.yml
git commit -m "Launch v4"
git push origin main
# This triggers deployment to both s3://v4.fring.io and s3://fring.io
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
- https://fring.io, https://www.fring.io → Latest version (v3)
- https://kfring.com, https://www.kfring.com → Latest version (v3)
- https://v4.fring.io → v4 (in development)
- https://v3.kfring.com → v3 (current live)
- https://v2.fring.io, https://v2.kfring.com → v2
- https://v1.fring.io, https://v1.kfring.com → v1

See [DEPLOYMENT_ARCHITECTURE.md](DEPLOYMENT_ARCHITECTURE.md) for complete details.
