# Infrastructure Management

This directory contains scripts and documentation for managing the fring.io infrastructure.

> **📚 For comprehensive infrastructure documentation, see [INFRASTRUCTURE.md](INFRASTRUCTURE.md)**

## Quick Reference

### Current Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub (main branch)                      │
│  sites/                                                      │
│    ├── v1/  (Jekyll, legacy)                                │
│    ├── v2/  (Minimal HTML)                                  │
│    └── v3/  (Current live) ← LATEST_VERSION                 │
│                                                              │
│  Push to main → GitHub Actions                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      AWS                                     │
│                                                              │
│  Content Buckets (host actual files):                       │
│    ├── fring.io         → Latest version (via CloudFront)   │
│    ├── v1.kfring.com    → v1 site                           │
│    ├── v2.fring.io      → v2 site                           │
│    └── v3.fring.io      → v3 site                           │
│                                                              │
│  Redirect Buckets (empty, HTTP 301):                        │
│    ├── kfring.com       → https://fring.io                  │
│    ├── www.kfring.com   → https://fring.io                  │
│    ├── v1.fring.io      → http://v1.kfring.com              │
│    ├── v2.kfring.com    → http://v2.fring.io                │
│    └── v3.kfring.com    → http://v3.fring.io                │
│                                                              │
│  CloudFront CDN (E2D0LEBFJYK5DC):                           │
│    ├── fring.io         (origin: fring.io S3 website)       │
│    └── www.fring.io     (origin: fring.io S3 website)       │
│                                                              │
│  Route53 DNS:                                               │
│    ├── fring.io zone    (Z02559231DI1MPZVK109K)             │
│    └── kfring.com zone  (Z3UYN92ABCCNG4)                    │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Workflow

### How it Works

1. **Push to main branch** with changes in `sites/vN/`
2. **GitHub Actions** detects changed version
3. **Deploys to versioned bucket**: `s3://vN.fring.io/`
4. **If version == LATEST_VERSION**: Also deploys to `s3://fring.io/` and invalidates CloudFront

### Current Live Version

**v3** (defined in `VERSION` file and `LATEST_VERSION` in `.github/workflows/deploy.yml`)

## Common Tasks

### Working on Current Version (v3)

```bash
# Edit files
cd sites/v3/
vim index.html

# Commit and deploy
git add sites/v3/
git commit -m "Update v3 design"
git push origin main
# Deploys to both v3.fring.io and fring.io (apex)
```

### Creating a New Version (v4)

```bash
# 1. Provision AWS infrastructure
./infrastructure/provision-site.sh v4

# 2. Create v4 directory
mkdir sites/v4
cp sites/v3/* sites/v4/

# 3. Make changes
cd sites/v4/
# Edit files...

# 4. Commit and push
git add sites/v4/
git commit -m "Add v4 site"
git push origin main
# Deploys to v4.fring.io only (not apex yet)
```

### Launching v4 as Live Version

See [LAUNCH_CHECKLIST.md](../LAUNCH_CHECKLIST.md) for complete procedure:

1. Update `VERSION` file → `echo "v4" > VERSION`
2. Update `LATEST_VERSION` in `.github/workflows/deploy.yml`
3. Update `README.md` "Current Live Version" section
4. Commit and push

## Prerequisites

### AWS Setup
1. AWS Account with appropriate permissions
2. Route53 hosted zones: `fring.io` and `kfring.com`
3. IAM user: `github-actions-deploy` with deployment permissions

### GitHub Secrets Required

```
AWS_ACCESS_KEY_ID             - IAM user access key
AWS_SECRET_ACCESS_KEY         - IAM user secret key
AWS_REGION                    - us-east-1
CLOUDFRONT_DISTRIBUTION_MAIN  - E2D0LEBFJYK5DC
```

## Provisioning a New Version

The `provision-site.sh` script automates infrastructure setup:

```bash
cd infrastructure
./provision-site.sh v4
```

This creates:
- **Primary bucket**: `v4.fring.io` (content hosting)
- **Redirect bucket**: `v4.kfring.com` (redirects to v4.fring.io)
- **DNS records**: Both CNAME records in Route53
- **Bucket policies**: Public read access
- **Website hosting**: Enabled with index.html

## Special Cases

### v1 (Legacy Jekyll Site)

v1 is special because it has hardcoded `http://v1.kfring.com` URLs in Jekyll `_config.yml`:

- **Source**: `sites/v1/_site/` (Jekyll build output)
- **Bucket**: `v1.kfring.com` (not v1.fring.io)
- **Redirect**: `v1.fring.io` → `v1.kfring.com`

Deployment workflow handles this automatically.

## Manual Operations

### Deploy Specific Version
```bash
# Deploy v3 to v3.fring.io
aws s3 sync sites/v3/ s3://v3.fring.io/ --delete

# Deploy to apex (if you're making it live)
aws s3 sync sites/v3/ s3://fring.io/ --delete

# Invalidate CloudFront
aws cloudfront create-invalidation \
  --distribution-id E2D0LEBFJYK5DC \
  --paths "/*"
```

### Check Bucket Contents
```bash
aws s3 ls s3://v3.fring.io/ --recursive
```

### Test Redirects
```bash
curl -I http://v3.kfring.com  # Should redirect to v3.fring.io
curl -I http://kfring.com     # Should redirect to fring.io
```

## Troubleshooting

### Changes Not Showing
1. Check GitHub Actions logs
2. Clear CloudFront cache (for apex domains)
3. Hard refresh browser (Cmd+Shift+R)
4. Wait for DNS propagation (5-15 min)

### 403 Forbidden
1. Check S3 bucket policy allows public read
2. Verify CloudFront origin uses S3 website endpoint (not S3 API)
3. Invalidate CloudFront cache

### Version Confusion
- Check `VERSION` file for current live version
- Check `LATEST_VERSION` in `.github/workflows/deploy.yml`
- See [INFRASTRUCTURE.md](INFRASTRUCTURE.md) for complete domain mapping

## Cost Estimate

- **S3 Storage**: ~$0.10/month (minimal files)
- **CloudFront**: Free tier covers most traffic
- **Route53**: $1.00/month (2 hosted zones)

**Total**: ~$2-3/month

## Documentation

- **[INFRASTRUCTURE.md](INFRASTRUCTURE.md)** - Complete infrastructure documentation
- **[LAUNCH_CHECKLIST.md](../LAUNCH_CHECKLIST.md)** - Version launch procedure
- **[README.md](../README.md)** - Project overview
- **[V3_FUTURE_ENHANCEMENTS.md](../V3_FUTURE_ENHANCEMENTS.md)** - Future improvements

## Security

- ✅ IAM users with least-privilege permissions
- ✅ AWS credentials in GitHub Secrets only
- ✅ S3 buckets block public write access
- ✅ CloudFront enforces HTTPS
- ✅ Git history cleaned of credentials (BFG)

## Additional Resources

- [AWS S3 Static Website Hosting](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)
- [CloudFront Documentation](https://docs.aws.amazon.com/cloudfront/)
- [Route53 Documentation](https://docs.aws.amazon.com/route53/)
