#!/bin/bash
set -euo pipefail

# provision-site.sh - Provision a new version of fring.io
# Usage: ./provision-site.sh <version> [--create-cloudfront]
#
# Example: ./provision-site.sh v4
#          ./provision-site.sh v5 --create-cloudfront

VERSION="${1:-}"
CREATE_CLOUDFRONT="${2:-}"
PRIMARY_DOMAIN="fring.io"
SECONDARY_DOMAIN="kfring.com"
PRIMARY_BUCKET="${VERSION}.${PRIMARY_DOMAIN}"
SECONDARY_BUCKET="${VERSION}.${SECONDARY_DOMAIN}"
AWS_REGION="${AWS_REGION:-us-east-1}"

if [[ -z "$VERSION" ]]; then
    echo "Usage: $0 <version> [--create-cloudfront]"
    echo "Example: $0 v4"
    exit 1
fi

echo "🚀 Provisioning ${VERSION} (${PRIMARY_DOMAIN} + ${SECONDARY_DOMAIN})..."

# 1. Create PRIMARY S3 bucket (fring.io - contains actual content)
echo "📦 Creating PRIMARY S3 bucket: ${PRIMARY_BUCKET}"
aws s3api create-bucket \
    --bucket "${PRIMARY_BUCKET}" \
    --region "${AWS_REGION}"

# Disable ACLs and use bucket policy instead
aws s3api put-public-access-block \
    --bucket "${PRIMARY_BUCKET}" \
    --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# 1b. Create SECONDARY S3 bucket (kfring.com - redirect to fring.io)
echo "📦 Creating SECONDARY S3 bucket (redirect): ${SECONDARY_BUCKET}"
aws s3api create-bucket \
    --bucket "${SECONDARY_BUCKET}" \
    --region "${AWS_REGION}"

# 2. Enable website hosting on PRIMARY bucket
echo "🌐 Enabling static website hosting on ${PRIMARY_BUCKET}..."
aws s3 website "s3://${PRIMARY_BUCKET}" \
    --index-document index.html \
    --error-document index.html

# 2b. Configure SECONDARY bucket to redirect to PRIMARY
echo "🔀 Configuring ${SECONDARY_BUCKET} to redirect to ${PRIMARY_BUCKET}..."
cat > /tmp/redirect-config.json <<EOF
{
  "RedirectAllRequestsTo": {
    "HostName": "${PRIMARY_BUCKET}"
  }
}
EOF

aws s3api put-bucket-website \
    --bucket "${SECONDARY_BUCKET}" \
    --website-configuration file:///tmp/redirect-config.json

# 3. Set bucket policy for public read (PRIMARY bucket only)
echo "🔓 Setting bucket policy for public read on ${PRIMARY_BUCKET}..."
cat > /tmp/bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::${PRIMARY_BUCKET}/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy \
    --bucket "${PRIMARY_BUCKET}" \
    --policy file:///tmp/bucket-policy.json

# 4. Enable CORS if needed (PRIMARY bucket only)
echo "🔀 Configuring CORS on ${PRIMARY_BUCKET}..."
cat > /tmp/cors-config.json <<EOF
{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["GET", "HEAD"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3600
    }
  ]
}
EOF

aws s3api put-bucket-cors \
    --bucket "${PRIMARY_BUCKET}" \
    --cors-configuration file:///tmp/cors-config.json

# 5. Create CloudFront distribution (optional)
if [[ "$CREATE_CLOUDFRONT" == "--create-cloudfront" ]]; then
    echo "☁️  Creating CloudFront distribution..."

    cat > /tmp/cloudfront-config.json <<EOF
{
  "CallerReference": "${BUCKET_NAME}-$(date +%s)",
  "Comment": "${BUCKET_NAME} distribution",
  "Enabled": true,
  "DefaultRootObject": "index.html",
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-${BUCKET_NAME}",
        "DomainName": "${BUCKET_NAME}.s3-website-${AWS_REGION}.amazonaws.com",
        "CustomOriginConfig": {
          "HTTPPort": 80,
          "HTTPSPort": 443,
          "OriginProtocolPolicy": "http-only"
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-${BUCKET_NAME}",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 2,
      "Items": ["GET", "HEAD"],
      "CachedMethods": {
        "Quantity": 2,
        "Items": ["GET", "HEAD"]
      }
    },
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {
        "Forward": "none"
      }
    },
    "MinTTL": 0,
    "DefaultTTL": 86400,
    "MaxTTL": 31536000,
    "Compress": true
  },
  "ViewerCertificate": {
    "CloudFrontDefaultCertificate": true
  },
  "Aliases": {
    "Quantity": 1,
    "Items": ["${BUCKET_NAME}"]
  }
}
EOF

    DISTRIBUTION_ID=$(aws cloudfront create-distribution \
        --distribution-config file:///tmp/cloudfront-config.json \
        --query 'Distribution.Id' \
        --output text)

    echo "✅ CloudFront Distribution ID: ${DISTRIBUTION_ID}"
    echo "   Add this to GitHub Secrets as CLOUDFRONT_DISTRIBUTION_VERSIONS"
fi

# 6. Create Route53 DNS records (both domains)
echo "🌍 Creating Route53 DNS records..."

# Get hosted zone IDs
KFRING_ZONE_ID=$(aws route53 list-hosted-zones \
    --query "HostedZones[?Name=='${PRIMARY_DOMAIN}.'].Id" \
    --output text | cut -d'/' -f3)

FRING_ZONE_ID=$(aws route53 list-hosted-zones \
    --query "HostedZones[?Name=='${SECONDARY_DOMAIN}.'].Id" \
    --output text | cut -d'/' -f3)

if [[ -z "$KFRING_ZONE_ID" ]] || [[ -z "$FRING_ZONE_ID" ]]; then
    echo "⚠️  Warning: Could not find hosted zones"
    echo "   Please create DNS records manually"
else
    # Create DNS record for PRIMARY domain (kfring.com)
    echo "📝 Creating DNS for ${PRIMARY_BUCKET}..."
    cat > /tmp/route53-primary.json <<EOF
{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "${PRIMARY_BUCKET}",
      "Type": "CNAME",
      "TTL": 300,
      "ResourceRecords": [{"Value": "${PRIMARY_BUCKET}.s3-website-${AWS_REGION}.amazonaws.com"}]
    }
  }]
}
EOF

    aws route53 change-resource-record-sets \
        --hosted-zone-id "${KFRING_ZONE_ID}" \
        --change-batch file:///tmp/route53-primary.json

    echo "✅ DNS created: ${PRIMARY_BUCKET}"

    # Create DNS record for SECONDARY domain (fring.io)
    echo "📝 Creating DNS for ${SECONDARY_BUCKET}..."
    cat > /tmp/route53-secondary.json <<EOF
{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "${SECONDARY_BUCKET}",
      "Type": "CNAME",
      "TTL": 300,
      "ResourceRecords": [{"Value": "${PRIMARY_BUCKET}"}]
    }
  }]
}
EOF

    aws route53 change-resource-record-sets \
        --hosted-zone-id "${FRING_ZONE_ID}" \
        --change-batch file:///tmp/route53-secondary.json

    echo "✅ DNS created: ${SECONDARY_BUCKET} (redirects to ${PRIMARY_BUCKET})"
fi

# 7. Summary
echo ""
echo "✅ Site provisioned successfully!"
echo ""
echo "📋 Summary:"
echo "   Primary Bucket:   ${PRIMARY_BUCKET} (content)"
echo "   Secondary Bucket: ${SECONDARY_BUCKET} (redirect)"
echo "   Region:           ${AWS_REGION}"
echo ""
echo "   🌐 Accessible at:"
echo "      http://${PRIMARY_BUCKET}"
echo "      http://${SECONDARY_BUCKET} (redirects to primary)"
echo ""
echo "📝 Next steps:"
echo "   1. Create git branch: git checkout -b ${VERSION}.fring.io"
echo "   2. Add your site files to the branch"
echo "   3. Push to GitHub: git push -u origin ${VERSION}.fring.io"
echo "   4. GitHub Actions will automatically deploy to ${PRIMARY_BUCKET}"
echo "   5. Site will be accessible at both:"
echo "      - ${PRIMARY_BUCKET} (primary)"
echo "      - ${SECONDARY_BUCKET} (auto-redirects)"
echo ""
if [[ "$CREATE_CLOUDFRONT" == "--create-cloudfront" ]]; then
    echo "   5. Wait for CloudFront distribution to deploy (~15 minutes)"
    echo "   6. Update DNS to point to CloudFront (optional)"
fi

# Cleanup
rm -f /tmp/bucket-policy.json /tmp/cors-config.json /tmp/cloudfront-config.json /tmp/redirect-config.json /tmp/route53-primary.json /tmp/route53-secondary.json
