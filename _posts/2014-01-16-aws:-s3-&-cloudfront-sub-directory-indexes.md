---
layout: post
title: "AWS: S3 & CloudFront sub-directory indexes"
<!--- modified: 2014-01-16 -->
category: how-to
tags: [aws, amazon, s3, cloudfront, websites, how-to]
description: "get them clean urls working.."
image:
  feature: feat/heuy.jpg
  credit: Craig Fring
  creditlink: http://www.flickr.com/photos/kfring/6994770678/
---

Ran into a frustrating problem while setting up this site with clean urls.

### Symptom

When in any directory other than root, such as **http://kfring.com/foo/** 
CloudFront refuses to display an **index.html** as default.  

#### What's going on?

CloudFront does not respect root document settings when pulling directly from an S3
Bucket.

#### Solution

Change the CloudFront origin point to the website version of your S3 bucket.

|---
| **Good** | **Bad**
| {% raw %}kfring.com.s3-website-us-east-1.amazonaws.com{% endraw %} | {% raw %}kfring.com.s3.amazonaws.com{% endraw %}


#### Result:

Clean URL's such as [{{ site.url }}/archives]({{ site.url }}/archives) can now work as expected.
