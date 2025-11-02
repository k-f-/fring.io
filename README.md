## Personal Website

What it says on the tin. 😉

**Live at**: https://fring.io

## Deployment

This site uses a dual-bucket deployment strategy:
- **Apex domains** (fring.io, kfring.com, www) → Always show the latest version
- **Versioned subdomains** (v4.fring.io) → Show specific versions

When you push to a version branch (e.g., `v4.fring.io`), GitHub Actions automatically deploys to:
1. The versioned bucket (s3://v4.fring.io)
2. The main bucket (s3://fring.io) for apex domains

See [DEPLOYMENT_ARCHITECTURE.md](DEPLOYMENT_ARCHITECTURE.md) for complete details.

## Version History

- **v4** (2024-present): TBD - Current version
- **v3** (2020-2024): Minimal design - http://v3.kfring.com
- **v2** (2015-2020): Minimal HTML - http://v2.kfring.com / http://v2.fring.io
- **v1** (2013-2015): Jekyll blog - http://v1.kfring.com / http://v1.fring.io

Old branches archived in `archive/*` tags.

## Infrastructure

See [infrastructure/](infrastructure/) directory for:
- IAM policies
- Provisioning scripts
- CloudFront configuration
