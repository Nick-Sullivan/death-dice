output "domain_name" {
  description = "The domain name of the public CloudFront URL, that points to the S3 bucket"
  value       = aws_cloudfront_distribution.s3_distribution.domain_name
}

output "hosted_zone_id" {
  description = "The hosted zone ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.s3_distribution.hosted_zone_id
}
