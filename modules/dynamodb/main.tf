resource "aws_dynamodb_table" "chatbot_sessions" {
  name         = "${var.project_name}-sessions-${var.environment}"
  billing_mode = var.billing_mode
  hash_key     = "sessionId"

  attribute {
    name = "sessionId"
    type = "S"
  }

  ttl {
    enabled        = true
    attribute_name = "ttl"
  }

  # Enable server-side encryption
  server_side_encryption {
    enabled     = true
    kms_key_arn = var.kms_key_arn
  }

  # Enable point-in-time recovery for disaster recovery
  point_in_time_recovery {
    enabled = var.enable_point_in_time_recovery
  }

  tags = {
    Name        = "${var.project_name}-sessions"
    Environment = var.environment
  }
}

resource "aws_dynamodb_table" "customer_data" {
  name         = "${var.project_name}-customers-${var.environment}"
  billing_mode = var.billing_mode
  hash_key     = "customerId"

  attribute {
    name = "customerId"
    type = "S"
  }

  # Enable server-side encryption
  server_side_encryption {
    enabled     = true
    kms_key_arn = var.kms_key_arn
  }

  # Enable point-in-time recovery for disaster recovery
  point_in_time_recovery {
    enabled = var.enable_point_in_time_recovery
  }

  tags = {
    Name        = "${var.project_name}-customers"
    Environment = var.environment
  }
}
