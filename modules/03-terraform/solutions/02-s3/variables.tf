variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "bucket_prefix" {
  type        = string
  description = "A unique prefix for the S3 bucket (use your name or handle)"
}

variable "environment" {
  type    = string
  default = "dev"
}
