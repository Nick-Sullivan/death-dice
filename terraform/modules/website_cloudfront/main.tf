# Creates a CloudFront distribution, with a verified certificate for SSL. AWS provider must be set to us-east-1.

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

resource "aws_acm_certificate" "https" {
  # Must be in us-east-1 for use by CloudFront
  domain_name               = var.domain_name
  subject_alternative_names = var.alternative_names
  validation_method         = "DNS"
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "https" {
  # Create CNAME entries to allow validation of the certificate
  for_each = {
    for dvo in aws_acm_certificate.https.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = var.zone_id
}

resource "aws_acm_certificate_validation" "https" {
  # Doesn't create anything, just waits until validation is complete.
  certificate_arn         = aws_acm_certificate.https.arn
  validation_record_fqdns = [for record in aws_route53_record.https : record.fqdn]
}

resource "aws_cloudfront_distribution" "s3_distribution" {
  # CloudFront distributions can take a few minutes to deploy
  depends_on = [aws_acm_certificate_validation.https]

  aliases             = concat([var.domain_name], var.alternative_names)
  comment             = "Online resume"
  default_root_object = "index.html"
  enabled             = true
  is_ipv6_enabled     = true
  price_class         = "PriceClass_All"

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "CV"
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 86400
    default_ttl            = 86400
    max_ttl                = 86400
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }

  origin {
    domain_name = var.s3_url
    origin_id   = "CV"
    custom_origin_config {
      http_port                = 80
      https_port               = 443
      origin_keepalive_timeout = 5
      origin_protocol_policy   = "http-only"
      origin_read_timeout      = 30
      origin_ssl_protocols = [
        "TLSv1",
        "TLSv1.1",
        "TLSv1.2",
      ]

    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn = aws_acm_certificate.https.arn
    ssl_support_method  = "sni-only"
  }
}
