# Infrastructure Management

This directory contains scripts and documentation for managing the fring.io infrastructure.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         GitHub                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │   main   │  │v3.fring.io│ │v4.fring.io│                  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                  │
│       │             │              │                         │
│       └─────────────┴──────────────┘                        │
│                     │                                        │
│              GitHub Actions                                 │
└─────────────────────┴───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      AWS                                     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  S3 Bucket   │  │  S3 Bucket   │  │  S3 Bucket   │      │
│  │  fring.io    │  │v3.fring.io   │  │v4.fring.io   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                  │               │
│         ▼                 ▼                  ▼               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              CloudFront CDN                         │    │
│  └─────────────────────┬───────────────────────────────┘    │
│                        │                                     │
│                        ▼                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Route53 DNS                            │    │
│  │  fring.io      ──>  CloudFront (main/latest)       │    │
│  │  www.fring.io  ──>  CloudFront (main/latest)       │    │
│  │  v3.fring.io   ──>  S3 Website Endpoint            │    │
│  │  v4.fring.io   ──>  S3 Website Endpoint            │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

## Deployment Workflow

### 1. Main Site (fring.io, www.fring.io)
- **Branch**: `main`
- **S3 Bucket**: `fring.io`
- **URLs**: `https://fring.io`, `https://www.fring.io`
- **Deployment**: Automatic on push to `main`

### 2. Version Sites (v3.fring.io, v4.fring.io, etc.)
- **Branch**: `v<N>.fring.io` (e.g., `v4.fring.io`)
- **S3 Bucket**: `v<N>.fring.io`
- **URL**: `https://v<N>.fring.io`
- **Deployment**: Automatic on push to version branch

## Prerequisites

### AWS Setup
1. AWS Account with appropriate permissions
2. Route53 hosted zone for `fring.io`
3. IAM user with deployment permissions (see SECURITY_REMEDIATION.md)

### GitHub Secrets Required
Add these secrets to your GitHub repository:

```
AWS_ACCESS_KEY_ID             - IAM user access key
AWS_SECRET_ACCESS_KEY         - IAM user secret key
AWS_REGION                    - Default: us-east-1
CLOUDFRONT_DISTRIBUTION_MAIN  - CloudFront distribution ID for main site
CLOUDFRONT_DISTRIBUTION_VERSIONS - CloudFront distribution ID for versioned sites (optional)
CLOUDFRONT_DOMAIN_MAIN        - CloudFront domain name (e.g., d1234abcd.cloudfront.net)
ROUTE53_HOSTED_ZONE_ID        - Route53 hosted zone ID for fring.io
```

## Provisioning a New Version Site

### Quick Start
```bash
# Provision v4.fring.io
cd infrastructure
chmod +x provision-site.sh
./provision-site.sh v4

# With CloudFront (recommended for production)
./provision-site.sh v4 --create-cloudfront
```

### Manual Steps
1. **Provision infrastructure**:
   ```bash
   ./infrastructure/provision-site.sh v4
   ```

2. **Create and checkout new branch**:
   ```bash
   git checkout -b v4.fring.io
   ```

3. **Add your site files**:
   ```bash
   # Copy your HTML, CSS, etc.
   cp /path/to/your/site/* .
   git add .
   git commit -m "Add v4 site"
   ```

4. **Push to GitHub**:
   ```bash
   git push -u origin v4.fring.io
   ```

5. **Deploy automatically via GitHub Actions**:
   - GitHub Actions will detect the push
   - Files will sync to S3
   - CloudFront cache will invalidate (if configured)
   - DNS will update automatically

## Promoting a Version to Main

When you want to make a version site (e.g., v4) the main site:

```bash
# 1. Checkout main branch
git checkout main

# 2. Merge version branch
git merge v4.fring.io

# 3. Push to main
git push origin main
```

GitHub Actions will automatically:
- Deploy to `fring.io` S3 bucket
- Update Route53 records for `fring.io` and `www.fring.io`
- Invalidate CloudFront cache

## Manual Deployment

If you need to deploy manually without GitHub Actions:

```bash
# Deploy to main site
aws s3 sync . s3://fring.io/ \
  --exclude ".git/*" \
  --exclude ".github/*" \
  --exclude "*.md" \
  --delete

# Deploy to version site
aws s3 sync . s3://v4.fring.io/ \
  --exclude ".git/*" \
  --exclude ".github/*" \
  --exclude "*.md" \
  --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*"
```

## Updating DNS Records

### Using AWS CLI
```bash
# Update main site DNS
aws route53 change-resource-record-sets \
  --hosted-zone-id YOUR_ZONE_ID \
  --change-batch file://infrastructure/dns-main.json

# Update version site DNS
aws route53 change-resource-record-sets \
  --hosted-zone-id YOUR_ZONE_ID \
  --change-batch file://infrastructure/dns-version.json
```

### Using AWS Console
1. Go to Route53 > Hosted zones > fring.io
2. Create/Edit record:
   - **Name**: `fring.io` or `v4.fring.io`
   - **Type**: A (Alias)
   - **Alias to**: CloudFront distribution or S3 website endpoint
   - **Routing policy**: Simple

## Cleanup/Decommissioning

To remove an old version site:

```bash
# 1. Delete S3 bucket contents
aws s3 rm s3://v3.fring.io/ --recursive

# 2. Delete S3 bucket
aws s3 rb s3://v3.fring.io

# 3. Delete Route53 record
aws route53 change-resource-record-sets \
  --hosted-zone-id YOUR_ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "DELETE",
      "ResourceRecordSet": {
        "Name": "v3.fring.io",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [{"Value": "..."}]
      }
    }]
  }'

# 4. Delete CloudFront distribution (if exists)
# Note: Must disable first, then delete after ~15 minutes
aws cloudfront update-distribution --id DIST_ID --if-match ETAG \
  --distribution-config '{"Enabled": false, ...}'
```

## Troubleshooting

### Deployment Fails
1. Check GitHub Actions logs
2. Verify AWS credentials in GitHub Secrets
3. Check IAM permissions
4. Verify bucket exists and is accessible

### DNS Not Updating
1. Check Route53 hosted zone exists
2. Verify `ROUTE53_HOSTED_ZONE_ID` secret is correct
3. DNS propagation can take up to 48 hours (usually <1 hour)

### CloudFront Cache Issues
1. Manually invalidate: `aws cloudfront create-invalidation --distribution-id ID --paths "/*"`
2. Check cache headers in S3 objects
3. Wait for invalidation to complete (~5 minutes)

### 403 Forbidden Errors
1. Check S3 bucket policy allows public read
2. Verify bucket website hosting is enabled
3. Check CloudFront origin settings

## Cost Optimization

- **S3**: ~$0.023/GB/month (first 50TB)
- **CloudFront**: ~$0.085/GB for first 10TB
- **Route53**: $0.50/hosted zone/month + $0.40/million queries
- **Data transfer**: Free from S3 to CloudFront

**Estimated monthly cost for personal site**: $0.50 - $2.00

### Tips to reduce costs:
1. Use CloudFront (free tier: 1TB data transfer/month)
2. Enable gzip/brotli compression
3. Set appropriate cache headers
4. Delete old version sites
5. Use S3 Intelligent-Tiering for infrequent access

## Security Checklist

- [ ] IAM user has least-privilege permissions
- [ ] AWS credentials stored in GitHub Secrets (not code)
- [ ] S3 buckets block public write access
- [ ] CloudFront uses HTTPS
- [ ] Route53 DNS locked (registrar lock)
- [ ] Billing alerts enabled
- [ ] CloudTrail logging enabled
- [ ] S3 versioning enabled (optional, for rollback)

## Additional Resources

- [AWS S3 Static Website Hosting](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)
- [CloudFront Documentation](https://docs.aws.amazon.com/cloudfront/)
- [Route53 Documentation](https://docs.aws.amazon.com/route53/)
- [GitHub Actions AWS Guide](https://github.com/aws-actions)
