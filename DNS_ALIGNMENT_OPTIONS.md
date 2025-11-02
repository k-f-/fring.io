# DNS Alignment Options - kfring.com ↔ fring.io

## Current State

**Main Sites (Already Aligned):**
- kfring.com ✅ → CloudFront → fring.io S3 bucket
- fring.io ✅ → CloudFront → fring.io S3 bucket

**Version Sites (NOT Aligned):**
- v1.kfring.com ✅ → v1.kfring.com S3 bucket (works)
- v2.kfring.com ✅ → v2.kfring.com S3 bucket (works)
- v1.fring.io ❌ → duckdns.org (your home services)
- v2.fring.io ❌ → duckdns.org (your home services)

**Problem:** Wildcard `*.fring.io` points to duckdns.org, so version sites can't use fring.io domain.

---

## Option 1: Keep Status Quo (Simplest)

**What:** Leave as-is, use kfring.com for version sites, fring.io for main site

**Pros:**
- No changes needed
- No conflicts with home services
- Already working

**Cons:**
- Inconsistent domain usage
- v1/v2.fring.io don't work

**Implementation:** Nothing to do

---

## Option 2: Explicit DNS Records (Recommended)

**What:** Create specific DNS records for v1.fring.io, v2.fring.io that override the wildcard

**How DNS precedence works:**
1. Exact match (v1.fring.io) beats wildcard (*.fring.io)
2. Create explicit A records for each version site
3. Wildcard still works for other subdomains (home services)

**Pros:**
- ✅ Both domains work for all sites
- ✅ Keeps wildcard for home services
- ✅ No bucket renaming needed
- ✅ Simple DNS changes only

**Cons:**
- Need to create DNS records for each version (v1, v2, v3, v4...)

**Implementation:**

```bash
# For fring.io zone (Z02559231DI1MPZVK109K)

# Create v1.fring.io → v1.kfring.com bucket
aws route53 change-resource-record-sets \
  --hosted-zone-id Z02559231DI1MPZVK109K \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "v1.fring.io",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [{"Value": "v1.kfring.com.s3-website-us-east-1.amazonaws.com"}]
      }
    }]
  }'

# Create v2.fring.io → v2.kfring.com bucket
aws route53 change-resource-record-sets \
  --hosted-zone-id Z02559231DI1MPZVK109K \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "v2.fring.io",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [{"Value": "v2.kfring.com.s3-website-us-east-1.amazonaws.com"}]
      }
    }]
  }'
```

**Result:**
- v1.fring.io → v1.kfring.com bucket (same content as v1.kfring.com)
- v2.fring.io → v2.kfring.com bucket (same content as v2.kfring.com)
- other.fring.io → duckdns.org (home services still work)

---

## Option 3: Create Mirror Buckets

**What:** Create v1.fring.io, v2.fring.io S3 buckets that redirect to kfring.com buckets

**Pros:**
- Clean separation
- Could eventually move content

**Cons:**
- ❌ More complex
- ❌ Double the buckets to manage
- ❌ Need to sync content or setup redirects
- ❌ Not worth the effort

**Implementation:** Not recommended

---

## Option 4: Move Version Sites to CloudFront

**What:** Put v1, v2 behind CloudFront (like main site), then use CloudFront aliases

**Pros:**
- ✅ HTTPS support
- ✅ Better caching
- ✅ Could serve same bucket on both domains

**Cons:**
- More complex setup
- Additional CloudFront distributions (or complex origin setup)
- Version sites rarely accessed, probably overkill

**Implementation:** Overkill for static archives

---

## Recommendation: Option 2

Create explicit DNS records for v1.fring.io and v2.fring.io that point to the existing S3 buckets.

### Why This Works Best:

1. **DNS Precedence:** Exact matches (v1.fring.io) override wildcards (*.fring.io)
2. **No bucket changes:** Keep existing v1.kfring.com, v2.kfring.com buckets
3. **Both domains work:** v1.kfring.com AND v1.fring.io serve same content
4. **Home services unaffected:** other.fring.io still goes to duckdns
5. **Future-proof:** Easy to add v3.fring.io, v4.fring.io later

### Implementation Plan:

```bash
# 1. Create v1.fring.io DNS record
aws route53 change-resource-record-sets \
  --hosted-zone-id Z02559231DI1MPZVK109K \
  --change-batch file://dns-v1-fring-io.json

# 2. Create v2.fring.io DNS record
aws route53 change-resource-record-sets \
  --hosted-zone-id Z02559231DI1MPZVK109K \
  --change-batch file://dns-v2-fring-io.json

# 3. Test after ~5 minutes (DNS propagation)
curl -I http://v1.fring.io
curl -I http://v2.fring.io
```

### For Future Versions (v3, v4):

When creating new version:
1. Create bucket: `v4.kfring.com` (keep legacy naming)
2. Create DNS records for BOTH:
   - `v4.kfring.com` → S3 bucket
   - `v4.fring.io` → S3 bucket (CNAME to same)

---

## Summary Table

| Domain | Currently Points To | Should Point To | Action |
|--------|---------------------|-----------------|--------|
| fring.io | CloudFront ✅ | CloudFront | No change |
| www.fring.io | CloudFront ✅ | CloudFront | No change |
| kfring.com | CloudFront ✅ | CloudFront | No change |
| www.kfring.com | kfring.com ✅ | kfring.com | No change |
| v1.kfring.com | S3 ✅ | S3 | No change |
| v2.kfring.com | S3 ✅ | S3 | No change |
| v1.fring.io | duckdns ❌ | v1.kfring.com S3 | **Create CNAME** |
| v2.fring.io | duckdns ❌ | v2.kfring.com S3 | **Create CNAME** |
| *.fring.io | duckdns ✅ | duckdns | No change (home services) |

**Total changes needed:** 2 DNS records (v1.fring.io, v2.fring.io)
