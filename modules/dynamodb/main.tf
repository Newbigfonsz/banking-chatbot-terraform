resource "aws_dynamodb_table" "chatbot_sessions" {
  name         = "banking-chatbot-sessions-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "sessionId"

  attribute {
    name = "sessionId"
    type = "S"
  }

  ttl {
    enabled        = true
    attribute_name = "ttl"
  }

  tags = {
    Name        = "banking-chatbot-sessions"
    Environment = var.environment
  }
}

resource "aws_dynamodb_table" "customer_data" {
  name         = "banking-chatbot-customers-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "customerId"

  attribute {
    name = "customerId"
    type = "S"
  }

  tags = {
    Name        = "banking-chatbot-customers"
    Environment = var.environment
  }
}
