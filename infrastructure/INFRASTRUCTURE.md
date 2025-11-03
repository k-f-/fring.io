# Infrastructure Documentation

Last Updated: 2025-11-03

## Overview

This document describes the complete AWS infrastructure for fring.io, including S3 buckets, CloudFront distributions, Route53 DNS, and deployment workflows.

## Domain Architecture

### Primary Domains

**fring.io** is the canonical domain for all modern versions (v2, v3, v4+) and apex.
**v1.kfring.com** is the canonical domain for v1 only (legacy Jekyll site).

### Domain Redirect Flow

```
User Request Flow:
==================

Apex Domains (Latest Version - Currently v3):
- https://fring.io → CloudFront → S3 (fring.io bucket)
- https://www.fring.io → CloudFront → S3 (fring.io bucket)
- https://kfring.com → S3 redirect → https://fring.io
- https://www.kfring.com → S3 redirect → https://fring.io

Versioned Sites (v2, v3, v4):
- https://v3.fring.io → S3 (v3.fring.io bucket - content)
- https://v3.kfring.com → S3 redirect → https://v3.fring.io
- https://v2.fring.io → S3 (v2.fring.io bucket - content)
- https://v2.kfring.com → S3 redirect → https://v2.fring.io

Legacy v1 (Special Case):
- https://v1.kfring.com → S3 (v1.kfring.com bucket - content)
- https://v1.fring.io → S3 redirect → https://v1.kfring.com
```

### Home Lab Wildcards

```
Wildcard DNS for non-website subdomains:
- *.fring.io → DuckDNS (1007shighlandparkave.duckdns.org)
- Specific website records (v1-v4, www) override the wildcard
```

## S3 Buckets

### Content Hosting Buckets

These buckets contain actual website files:

| Bucket | Purpose | Size | Public Access |
|--------|---------|------|---------------|
| `fring.io` | Apex domain (latest version) | ~25 KB | ✅ Yes (public bucket policy) |
| `v1.kfring.com` | v1 legacy site | ~1 MB | ✅ Yes (public bucket policy) |
| `v2.fring.io` | v2 site | ~1 MB | ✅ Yes (public bucket policy) |
| `v3.fring.io` | v3 site | ~25 KB | ✅ Yes (public bucket policy) |

**Website Configuration:** Static website hosting enabled with `index.html` as index document.

**Bucket Policies:** All content hosting buckets have public read policies:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::BUCKET_NAME/*"
  }]
}
```

### Redirect Buckets

These buckets are EMPTY and only contain redirect configuration:

| Bucket | Redirects To | Purpose |
|--------|--------------|---------|
| `kfring.com` | `https://fring.io` | Apex domain redirect |
| `www.kfring.com` | `https://fring.io` | WWW redirect |
| `v1.fring.io` | `http://v1.kfring.com` | v1 cross-domain redirect |
| `v2.kfring.com` | `http://v2.fring.io` | v2 legacy domain redirect |
| `v3.kfring.com` | `http://v3.fring.io` | v3 legacy domain redirect |

**Website Configuration:** Redirect all requests to target hostname.

**No Bucket Policy Needed:** Empty redirect buckets don't require public policies.

## CloudFront Distribution

**Distribution ID:** `E2D0LEBFJYK5DC`
**Domain:** `d8hzwjf71bq0x.cloudfront.net`

### Configuration

- **Aliases:** `fring.io`, `www.fring.io`
- **Origin:** `fring.io.s3-website-us-east-1.amazonaws.com` (S3 website endpoint)
- **Origin Protocol:** HTTP only (S3 website endpoints don't support HTTPS)
- **Viewer Protocol:** HTTPS redirect (users always get HTTPS)
- **SSL Certificate:** AWS Certificate Manager (ACM) for fring.io

### Why S3 Website Endpoint (Not S3 API)?

CloudFront uses the S3 **website endpoint** rather than the S3 API endpoint because:

1. **Directory Index Support:** S3 website endpoints handle `/about/` → `/about/index.html` automatically
2. **Custom Error Pages:** Proper 404 handling
3. **Redirects:** Supports S3 redirect rules

**Important:** When using S3 website endpoints, you MUST:
- Use `CustomOriginConfig` in CloudFront (not `S3OriginConfig`)
- Have a public bucket policy (OAI/OAC doesn't work with website endpoints)
- Use `http-only` origin protocol policy

## Route53 DNS

### Hosted Zones

- **fring.io** (Zone ID: Z02559231DI1MPZVK109K)
- **kfring.com** (Zone ID: Z3UYN92ABCCNG4)

### DNS Records

#### fring.io Zone

| Record | Type | Value | Purpose |
|--------|------|-------|---------|
| `fring.io` | A (Alias) | CloudFront (d8hzwjf71bq0x.cloudfront.net) | Apex to CDN |
| `www.fring.io` | A (Alias) | CloudFront (d8hzwjf71bq0x.cloudfront.net) | WWW to CDN |
| `*.fring.io` | CNAME | 1007shighlandparkave.duckdns.org | Home lab wildcard |
| `v1.fring.io` | CNAME | v1.kfring.com | v1 redirect |
| `v2.fring.io` | CNAME | v2.fring.io.s3-website-us-east-1.amazonaws.com | v2 site |
| `v3.fring.io` | CNAME | v3.fring.io.s3-website-us-east-1.amazonaws.com | v3 site |

#### kfring.com Zone

| Record | Type | Value | Purpose |
|--------|------|-------|---------|
| `kfring.com` | A (Alias) | s3-website-us-east-1.amazonaws.com | Redirect bucket |
| `www.kfring.com` | A (Alias) | s3-website-us-east-1.amazonaws.com | Redirect bucket |
| `v1.kfring.com` | A (Alias) | s3-website-us-east-1.amazonaws.com | v1 site |
| `v2.kfring.com` | CNAME | v2.fring.io | v2 redirect |
| `v3.kfring.com` | CNAME | v3.fring.io | v3 redirect |

## Deployment Workflow

### GitHub Actions: `.github/workflows/deploy.yml`

**Triggers:**
- Push to `main` branch with changes in `sites/**`
- Manual workflow dispatch

**Process:**

1. **Detect version:** Analyze changed files or use manual input
2. **Deploy to versioned bucket:**
   - v1: Deploy `sites/v1/_site/` → `s3://v1.kfring.com/`
   - v2+: Deploy `sites/v{N}/` → `s3://v{N}.fring.io/`
3. **Deploy to apex (if latest version):**
   - Copy content → `s3://fring.io/`
   - Invalidate CloudFront cache
4. **Set cache headers:**
   - HTML: `max-age=3600` (1 hour)
   - CSS/JS: `max-age=31536000, immutable` (1 year)

### Special Case: v1 (Legacy)

**Why v1 is different:**

v1 is a Jekyll static site built in ~2014-2015 with hardcoded URLs in `_config.yml`:
```yaml
url: http://v1.kfring.com
```

This means ALL generated HTML files have absolute URLs like:
```html
<link rel="stylesheet" href="http://v1.kfring.com/assets/css/main.min.css">
```

**Therefore:**
- v1 MUST be hosted at `v1.kfring.com` (not v1.fring.io)
- Deployment uses `sites/v1/_site/` directory (Jekyll build output)
- v1.fring.io redirects to v1.kfring.com

**To rebuild v1:**
1. Edit `sites/v1/_config.yml` (already set to v1.kfring.com)
2. Jekyll would need to be installed to rebuild
3. Current approach: Direct HTML edits with sed if needed

## Security & Access

### S3 Bucket Policies

- **Content buckets:** Public read access (required for S3 website endpoints)
- **Redirect buckets:** No policy needed (empty, just redirect config)
- **Block Public Access:** Disabled on all buckets

### CloudFront

- **Origin Access:** No OAI/OAC (incompatible with S3 website endpoints)
- **SSL/TLS:** Viewer-side HTTPS only (origin uses HTTP)
- **Geo Restrictions:** None

### DNS

- **DNSSEC:** Not enabled
- **Zone Protection:** AWS IAM controls access to Route53

## Cost Optimization

### S3 Storage

- **Redirect buckets:** $0 (empty buckets)
- **Content buckets:** ~$0.10/month (minimal storage)

### Data Transfer

- **CloudFront:** Free tier covers most traffic
- **S3 → CloudFront:** Free (AWS internal transfer)
- **CloudFront → User:** First 1TB/month free

### DNS

- **Route53:** $0.50/hosted zone/month × 2 zones = $1.00/month
- **Queries:** $0.40/million queries (negligible for personal site)

**Total estimated cost: ~$2-3/month**

## Disaster Recovery

### Content Backup

- **Primary backup:** Git repository (all source files)
- **S3 versioning:** Not enabled (not needed - git is source of truth)
- **CloudFront cache:** Acts as temporary backup during incidents

### DNS Backup

- **Route53 records:** Exported and stored in git (manual process)
- **Registrar:** CloudFlare (domains registered separately)

### Recovery Process

1. **Full site loss:** Redeploy from git via GitHub Actions
2. **DNS loss:** Recreate hosted zones and import records
3. **CloudFront loss:** Recreate distribution (30-60 min propagation)

## Monitoring

### Current Monitoring

- ❌ No automated monitoring currently configured
- ❌ No uptime checks
- ❌ No alerting

### Recommended Monitoring (Future)

- [ ] AWS CloudWatch alarms for CloudFront errors
- [ ] External uptime monitoring (UptimeRobot, Pingdom, etc.)
- [ ] S3 access logging to track traffic
- [ ] CloudFront access logs for debugging

## Future Improvements

### Short Term

- [ ] Enable S3 access logging
- [ ] Set up uptime monitoring
- [ ] Create automated backup/export of Route53 records
- [ ] Add health checks to Route53

### Long Term

- [ ] Consider switching to CloudFront Functions for redirects (reduce S3 buckets)
- [ ] Implement automated Jekyll rebuild for v1 in CI/CD
- [ ] Consider CDN alternatives (Cloudflare, Fastly) for cost comparison
- [ ] Add CSP, security headers via CloudFront Functions

## Troubleshooting

### Common Issues

**403 Forbidden from CloudFront:**
- Check: S3 bucket policy allows public read
- Check: CloudFront origin uses S3 website endpoint (not S3 API)
- Fix: Invalidate CloudFront cache after policy changes

**404 for subdirectories (e.g., /about/):**
- Check: Using S3 website endpoint (not S3 API endpoint)
- S3 API endpoints don't support directory indexes

**Redirect loops:**
- Check: DNS for redirect buckets points to correct S3 website endpoint
- Check: S3 redirect configuration has correct target hostname

**v1 CSS/JS not loading:**
- Check: Files exist in v1.kfring.com bucket
- Check: HTML has correct URLs (http://v1.kfring.com/...)
- Fix: Re-run sed replacement and redeploy

### Useful Commands

```bash
# Check bucket contents
aws s3 ls s3://BUCKET_NAME/ --recursive

# Check bucket website configuration
aws s3api get-bucket-website --bucket BUCKET_NAME

# Check bucket policy
aws s3api get-bucket-policy --bucket BUCKET_NAME

# Test S3 website endpoint
curl -I http://BUCKET_NAME.s3-website-us-east-1.amazonaws.com/

# Check DNS resolution
dig +short DOMAIN_NAME

# Get CloudFront distribution info
aws cloudfront get-distribution --id DISTRIBUTION_ID

# Create CloudFront invalidation
aws cloudfront create-invalidation --distribution-id DISTRIBUTION_ID --paths "/*"
```

## References

- [S3 Website Endpoints](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteEndpoints.html)
- [CloudFront with S3 Origins](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/DownloadDistS3AndCustomOrigins.html)
- [Route53 Alias Records](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resource-record-sets-choosing-alias-non-alias.html)
