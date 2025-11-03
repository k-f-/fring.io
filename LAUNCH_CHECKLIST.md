# Launch Checklist

Use this checklist when making a new version live at fring.io.

## Prerequisites

- [ ] New version is tested and ready (e.g., v4)
- [ ] AWS infrastructure is provisioned (`./infrastructure/provision-site.sh v4`)
- [ ] DNS records are configured in Route53
- [ ] S3 buckets exist and have content

## Launch Steps

### 1. Update Version References

Update these three files to reference the new live version:

- [ ] **VERSION file** (repo root)
  ```bash
  echo "v4" > VERSION
  ```

- [ ] **.github/workflows/deploy.yml**
  ```bash
  # Change line 21:
  # From: LATEST_VERSION: v3
  # To:   LATEST_VERSION: v4
  ```

- [ ] **README.md**
  ```bash
  # Update "Current Live Version" section:
  # From: **🟢 v3**
  # To:   **🟢 v4**
  ```

### 2. Commit and Deploy

```bash
git add VERSION .github/workflows/deploy.yml README.md
git commit -m "Launch v4 as live version

Makes v4 the canonical version at fring.io and www.fring.io.
Previous version (v3) remains accessible at v3.fring.io."
git push origin main
```

This triggers GitHub Actions to:
1. Deploy v4 to `s3://v4.fring.io/`
2. Deploy v4 to `s3://fring.io/` (apex)
3. Invalidate CloudFront cache

### 3. Verify Deployment

Wait 2-5 minutes for deployment to complete, then verify:

- [ ] Check GitHub Actions run completed successfully
- [ ] Visit https://fring.io (should show v4 content)
- [ ] Visit https://www.fring.io (should show v4 content)
- [ ] Visit https://v4.fring.io (should show v4 content)
- [ ] Visit https://v3.fring.io (should still show v3 content)
- [ ] Check browser console for any errors
- [ ] Test on mobile device

### 4. Post-Launch

- [ ] Update infrastructure/INFRASTRUCTURE.md if needed
- [ ] Announce on social media (optional)
- [ ] Monitor CloudWatch for any errors (optional)

## Rollback

If something goes wrong, rollback to previous version:

```bash
echo "v3" > VERSION
# Update .github/workflows/deploy.yml back to LATEST_VERSION: v3
# Update README.md back to v3
git add VERSION .github/workflows/deploy.yml README.md
git commit -m "Rollback to v3"
git push origin main
```

## Version History

| Version | Launch Date | Notes |
|---------|-------------|-------|
| v3 | 2020-11 | Refined minimal design, current live version |
| v2 | 2015-10 | Minimal HTML |
| v1 | 2013-05 | Jekyll blog (legacy, uses kfring.com) |

## Notes

- **v1 is special:** Uses v1.kfring.com (not v1.fring.io) due to hardcoded Jekyll URLs
- **All versions remain accessible:** v2, v3, etc. continue to work at their versioned URLs
- **DNS propagation:** Changes to apex domains may take 5-15 minutes due to CloudFront caching
- **Old content cached:** Users may need hard refresh (Ctrl+Shift+R) to see new version
