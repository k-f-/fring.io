# Deployment Architecture

## Overview

This document describes how the fring.io site deployment works across multiple domains and versions.

## Domain Strategy

### Apex Domains (Always Latest Version)
- **fring.io** → CloudFront E2D0LEBFJYK5DC → S3 bucket `fring.io`
- **www.fring.io** → CloudFront E2D0LEBFJYK5DC → S3 bucket `fring.io`
- **kfring.com** → CloudFront E2D0LEBFJYK5DC → S3 bucket `fring.io`
- **www.kfring.com** → Alias to kfring.com → CloudFront → S3 bucket `fring.io`

When you deploy a new version, the apex domains automatically show the latest content.

### Versioned Subdomains (Specific Versions)
- **v4.fring.io** → S3 bucket `v4.fring.io` (static website)
- **v4.kfring.com** → S3 bucket `v4.kfring.com` (redirects to v4.fring.io)
- **v3.kfring.com** → S3 bucket `v3.kfring.com` (static website)
- **v2.kfring.com** → S3 bucket `v2.kfring.com` (static website)
- **v2.fring.io** → S3 bucket `v2.fring.io` (redirects to v2.kfring.com)
- **v1.kfring.com** → S3 bucket `v1.kfring.com` (static website)
- **v1.fring.io** → S3 bucket `v1.fring.io` (redirects to v1.kfring.com)

### Special Wildcard
- **\*.fring.io** → DuckDNS (for home services)
  - Explicit DNS records override this wildcard
  - v1.fring.io, v2.fring.io, etc. have explicit CNAME records

## Deployment Flow

### Automatic Deployment (GitHub Actions)

When you push to a version branch (e.g., `v4.fring.io`):

1. **Versioned Bucket**: Content syncs to `s3://v4.fring.io`
   - Accessible at https://v4.fring.io

2. **Main Bucket**: Same content syncs to `s3://fring.io`
   - Updates https://fring.io (via CloudFront)
   - Updates https://www.fring.io (via CloudFront)
   - Updates https://kfring.com (via CloudFront)
   - Updates https://www.kfring.com (via CloudFront)

3. **CloudFront Invalidation**: Cache cleared for instant updates

### Manual Deployment

You can also deploy manually using workflow_dispatch in GitHub Actions.

## Infrastructure Setup

### For New Versions

Use `infrastructure/provision-site.sh`:

```bash
./infrastructure/provision-site.sh v5
```

This automatically creates:
- **Primary bucket**: v5.fring.io (contains content)
- **Secondary bucket**: v5.kfring.com (redirects to v5.fring.io)
- **DNS records**: Both CNAME records in Route53
- **Policies**: Public read access, CORS, etc.

### Git Branch Strategy

- **main** branch: Infrastructure files only (never auto-deploys)
- **v4.fring.io** branch: v4 site content (auto-deploys on push)
- **v5.fring.io** branch: v5 site content (auto-deploys on push)
- Archive tags: `archive/v1.kfring.com`, `archive/v2.kfring.com`

## Version History

### v1 (Legacy - 2013-2015)
- Jekyll blog
- Primary: v1.kfring.com
- Secondary: v1.fring.io → redirects to v1.kfring.com

### v2 (Legacy - 2015-2020)
- Minimal HTML
- Primary: v2.kfring.com
- Secondary: v2.fring.io → redirects to v2.kfring.com

### v3 (2020-2024)
- Refined minimal design
- Primary: v3.kfring.com
- No v3.fring.io subdomain (existed before DNS alignment)

### v4+ (2024+)
- New primary domain: fring.io
- Primary: v4.fring.io (contains content)
- Secondary: v4.kfring.com → redirects to v4.fring.io

## AWS Resources

### S3 Buckets
- `fring.io` - Main bucket (apex domains point here via CloudFront)
- `v4.fring.io` - v4 versioned site
- `v4.kfring.com` - Redirects to v4.fring.io
- `v3.kfring.com` - v3 versioned site
- `v2.fring.io`, `v2.kfring.com` - v2 sites
- `v1.fring.io`, `v1.kfring.com` - v1 sites

### CloudFront
- **Distribution ID**: E2D0LEBFJYK5DC
- **Domain**: d8hzwjf71bq0x.cloudfront.net
- **Origin**: fring.io.s3.amazonaws.com
- **Aliases**: fring.io, www.fring.io, kfring.com

### Route53 Hosted Zones
- **fring.io** (Z02559231DI1MPZVK109K)
- **kfring.com** (Z3UYN92ABCCNG4)

## GitHub Secrets

Required secrets for deployment:
- `AWS_ACCESS_KEY_ID` - IAM user for deployment
- `AWS_SECRET_ACCESS_KEY` - IAM credentials
- `AWS_REGION` - us-east-1
- `CLOUDFRONT_DISTRIBUTION_MAIN` - E2D0LEBFJYK5DC
- `CLOUDFRONT_DOMAIN_MAIN` - d8hzwjf71bq0x.cloudfront.net

## Security

- Git history cleaned of AWS credentials (using BFG)
- IAM users:
  - `github-actions-deploy` - Minimal permissions for CI/CD
  - `kf-local-dev` - Full permissions for local development
- All secrets stored in GitHub Secrets
- Push protection enabled to prevent credential leaks
