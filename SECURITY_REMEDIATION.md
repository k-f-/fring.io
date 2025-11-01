# Security Remediation Plan

## Issue
AWS credentials were committed to public git history in `s3_website.yml` (archive/v1.kfring.com tag).

## Exposed Credentials
- AWS Access Key ID: `AKIA****************` (redacted - already rotated)
- AWS Secret Access Key: `****************************************` (redacted - already rotated)
- CloudFront Distribution ID: `E1OWBI1GERP2C0`

## Immediate Actions Required

### 1. Rotate AWS Credentials (DO THIS FIRST)
```bash
# Login to AWS Console
# Go to: IAM > Users > [your user] > Security credentials
# 1. Create new access key
# 2. Delete the old access key (the exposed one)
# 3. Save the new credentials securely
```

### 2. Audit AWS Activity
```bash
# Check CloudTrail for suspicious activity
# Go to: CloudTrail > Event history
# Filter by: User name = [IAM user that owned these keys]
# Date range: Last 6 months
# Look for:
#   - Unexpected API calls
#   - S3 bucket modifications
#   - EC2 instance launches
#   - IAM permission changes
```

### 3. Review AWS Billing
```bash
# Go to: Billing Dashboard
# Check for unexpected charges, especially:
#   - EC2 instances
#   - Data transfer
#   - S3 storage/requests
```

### 4. Set Up Least-Privilege IAM User
Create a new IAM user specifically for GitHub Actions with minimal permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket",
        "s3:PutBucketWebsite",
        "s3:PutBucketPolicy",
        "s3:GetBucketPolicy"
      ],
      "Resource": [
        "arn:aws:s3:::*.fring.io",
        "arn:aws:s3:::*.fring.io/*",
        "arn:aws:s3:::fring.io",
        "arn:aws:s3:::fring.io/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudfront:CreateInvalidation",
        "cloudfront:GetInvalidation",
        "cloudfront:ListInvalidations"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "route53:ChangeResourceRecordSets",
        "route53:ListResourceRecordSets",
        "route53:GetHostedZone"
      ],
      "Resource": "arn:aws:route53:::hostedzone/*"
    }
  ]
}
```

### 5. Add Credentials to GitHub Secrets
```bash
# Go to: GitHub repo > Settings > Secrets and variables > Actions
# Add these secrets:
#   - AWS_ACCESS_KEY_ID (new key)
#   - AWS_SECRET_ACCESS_KEY (new secret)
#   - AWS_REGION (e.g., us-east-1)
#   - CLOUDFRONT_DISTRIBUTION_ID (for cache invalidation)
#   - ROUTE53_HOSTED_ZONE_ID (your domain's hosted zone)
```

## Long-term Security Best Practices

### 1. Never Commit Secrets
- Add to `.gitignore`:
  ```
  *.env
  .env.*
  *_secret*
  *secrets*
  s3_website.yml
  ```

### 2. Use Git-Secrets or Gitleaks
```bash
brew install gitleaks
gitleaks detect --source . --verbose
```

### 3. Enable AWS Organizations SCPs
Set up Service Control Policies to prevent:
- Crypto mining
- Expensive service usage
- Region restrictions

### 4. Set Up AWS Billing Alerts
```bash
# Go to: CloudWatch > Alarms > Billing
# Create alarm for charges > $10/month
```

### 5. Consider AWS Secrets Manager or SSM Parameter Store
For any future secrets, use AWS native secret management instead of GitHub secrets.

## Git History Cleanup (Optional)
Note: This requires force-pushing and will break existing clones.

```bash
# Using BFG Repo-Cleaner
brew install bfg
bfg --delete-files s3_website.yml
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force --all
git push --force --tags
```

**Warning**: Only do this if you understand the implications. It will rewrite history.

## Verification Checklist
- [ ] Old AWS credentials rotated/deleted
- [ ] CloudTrail audited for suspicious activity
- [ ] Billing reviewed for unexpected charges
- [ ] New IAM user created with least-privilege permissions
- [ ] GitHub secrets configured
- [ ] `.gitignore` updated
- [ ] Git-secrets or Gitleaks configured
- [ ] Billing alerts enabled
- [ ] Team members notified (if applicable)
