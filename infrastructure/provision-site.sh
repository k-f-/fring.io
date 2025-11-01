#!/bin/bash
set -euo pipefail

# provision-site.sh - Provision a new version of fring.io
# Usage: ./provision-site.sh <version> [--create-cloudfront]
#
# Example: ./provision-site.sh v4
#          ./provision-site.sh v5 --create-cloudfront

VERSION="${1:-}"
CREATE_CLOUDFRONT="${2:-}"
DOMAIN="fring.io"
BUCKET_NAME="${VERSION}.${DOMAIN}"
AWS_REGION="${AWS_REGION:-us-east-1}"

if [[ -z "$VERSION" ]]; then
    echo "Usage: $0 <version> [--create-cloudfront]"
    echo "Example: $0 v4"
    exit 1
fi

echo "🚀 Provisioning ${BUCKET_NAME}..."

# 1. Create S3 bucket
echo "📦 Creating S3 bucket: ${BUCKET_NAME}"
aws s3api create-bucket \
    --bucket "${BUCKET_NAME}" \
    --region "${AWS_REGION}" \
    --acl public-read

# 2. Enable website hosting
echo "🌐 Enabling static website hosting..."
aws s3 website "s3://${BUCKET_NAME}" \
    --index-document index.html \
    --error-document index.html

# 3. Set bucket policy for public read
echo "🔓 Setting bucket policy for public read..."
cat > /tmp/bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::${BUCKET_NAME}/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy \
    --bucket "${BUCKET_NAME}" \
    --policy file:///tmp/bucket-policy.json

# 4. Enable CORS if needed
echo "🔀 Configuring CORS..."
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
    --bucket "${BUCKET_NAME}" \
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

# 6. Create Route53 DNS record
echo "🌍 Creating Route53 DNS record..."
HOSTED_ZONE_ID=$(aws route53 list-hosted-zones \
    --query "HostedZones[?Name=='${DOMAIN}.'].Id" \
    --output text | cut -d'/' -f3)

if [[ -z "$HOSTED_ZONE_ID" ]]; then
    echo "⚠️  Warning: Could not find hosted zone for ${DOMAIN}"
    echo "   Please create DNS record manually"
else
    # Get S3 website endpoint
    WEBSITE_ENDPOINT="${BUCKET_NAME}.s3-website-${AWS_REGION}.amazonaws.com"

    cat > /tmp/route53-change.json <<EOF
{
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "${BUCKET_NAME}",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [
          {
            "Value": "${WEBSITE_ENDPOINT}"
          }
        ]
      }
    }
  ]
}
EOF

    aws route53 change-resource-record-sets \
        --hosted-zone-id "${HOSTED_ZONE_ID}" \
        --change-batch file:///tmp/route53-change.json

    echo "✅ DNS record created: ${BUCKET_NAME} -> ${WEBSITE_ENDPOINT}"
fi

# 7. Summary
echo ""
echo "✅ Site provisioned successfully!"
echo ""
echo "📋 Summary:"
echo "   Bucket:      ${BUCKET_NAME}"
echo "   Region:      ${AWS_REGION}"
echo "   Website URL: http://${BUCKET_NAME}.s3-website-${AWS_REGION}.amazonaws.com"
echo "   Domain URL:  http://${BUCKET_NAME}"
echo ""
echo "📝 Next steps:"
echo "   1. Create git branch: git checkout -b ${VERSION}.fring.io"
echo "   2. Add your site files to the branch"
echo "   3. Push to GitHub: git push -u origin ${VERSION}.fring.io"
echo "   4. GitHub Actions will automatically deploy to S3"
echo ""
if [[ "$CREATE_CLOUDFRONT" == "--create-cloudfront" ]]; then
    echo "   5. Wait for CloudFront distribution to deploy (~15 minutes)"
    echo "   6. Update DNS to point to CloudFront (optional)"
fi

# Cleanup
rm -f /tmp/bucket-policy.json /tmp/cors-config.json /tmp/cloudfront-config.json /tmp/route53-change.json
