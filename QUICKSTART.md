# Quick Start Guide

## 🚨 Security First

**STOP!** Before doing anything else:

1. **Rotate AWS credentials** (exposed in git history)
   - Go to AWS Console > IAM > Users > Security credentials
   - Delete old access key (see SECURITY_REMEDIATION.md for details)
   - Create new access key
   - Save credentials securely

2. **Check for unauthorized AWS usage**
   - CloudTrail: Look for suspicious API calls
   - Billing: Check for unexpected charges

See `SECURITY_REMEDIATION.md` for detailed steps.

## Setup GitHub Secrets

Go to GitHub repo > Settings > Secrets and variables > Actions

Add these secrets:
```
AWS_ACCESS_KEY_ID               (new key from IAM)
AWS_SECRET_ACCESS_KEY           (new secret from IAM)
AWS_REGION                      us-east-1
CLOUDFRONT_DISTRIBUTION_MAIN    (your CloudFront distribution ID)
CLOUDFRONT_DOMAIN_MAIN          (e.g., d1234abcd.cloudfront.net)
ROUTE53_HOSTED_ZONE_ID          (your Route53 hosted zone ID)
```

Optional:
```
CLOUDFRONT_DISTRIBUTION_VERSIONS (for versioned sites)
```

## Create v4 Site

### 1. Provision Infrastructure
```bash
cd infrastructure
./provision-site.sh v4
```

This creates:
- S3 bucket: `v4.fring.io`
- S3 website hosting enabled
- Public read permissions
- DNS record: `v4.fring.io`

### 2. Create Git Branch
```bash
git checkout -b v4.fring.io
```

### 3. Build Your Site
Create your `index.html` and other files in the branch root.

See `V4_SITE_PLAN.md` for design ideas.

### 4. Deploy
```bash
git add .
git commit -m "Add v4 site"
git push -u origin v4.fring.io
```

GitHub Actions will automatically:
- Sync files to S3
- Set cache headers
- Invalidate CloudFront (if configured)

### 5. Verify
Visit `http://v4.fring.io` (may take a few minutes for DNS)

## Promote v4 to Main

When ready to make v4 the main site:

```bash
git checkout main
git merge v4.fring.io
git push origin main
```

This will:
- Deploy to `fring.io` bucket
- Update `fring.io` and `www.fring.io` DNS
- Make v4 your live site

## File Structure

```
fring.io/
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions deployment
├── infrastructure/
│   ├── provision-site.sh       # Provision new version
│   └── README.md               # Infrastructure docs
├── SECURITY_REMEDIATION.md     # Security steps
├── V4_SITE_PLAN.md            # v4 design plan
├── QUICKSTART.md              # This file
├── .gitignore                 # Ignore secrets
└── README.md                  # Project overview

# On v4.fring.io branch:
├── index.html                 # Your site
├── css/                       # Stylesheets
└── ...                        # Other assets
```

## Common Commands

```bash
# Deploy manually to v4
aws s3 sync . s3://v4.fring.io/ --exclude ".git/*" --delete

# Deploy manually to main
aws s3 sync . s3://fring.io/ --exclude ".git/*" --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id YOUR_ID \
  --paths "/*"

# Check DNS
dig v4.fring.io
dig fring.io

# List S3 buckets
aws s3 ls

# Check git branches
git branch -a
```

## Troubleshooting

**GitHub Actions failing?**
- Check secrets are set correctly
- View Actions tab for error logs
- Verify IAM permissions

**Site not loading?**
- Wait for DNS propagation (up to 1 hour)
- Check S3 bucket website hosting is enabled
- Verify bucket policy allows public read

**403 Forbidden?**
- Check S3 bucket policy
- Verify files are public-read
- Check CloudFront origin settings

**Changes not showing?**
- Clear CloudFront cache
- Check cache headers
- Hard refresh browser (Cmd+Shift+R)

## Resources

- Infrastructure docs: `infrastructure/README.md`
- Security guide: `SECURITY_REMEDIATION.md`
- v4 design plan: `V4_SITE_PLAN.md`
- AWS S3 docs: https://docs.aws.amazon.com/s3/
- GitHub Actions: https://docs.github.com/actions

## Support

- AWS issues: Check CloudTrail, IAM permissions
- GitHub issues: https://github.com/k-f-/fring.io/issues
- DNS issues: Check Route53, wait for propagation
