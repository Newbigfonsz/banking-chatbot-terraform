# Data source to create Lambda deployment package
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/functions/index.py"
  output_path = "${path.module}/functions/chatbot_handler.zip"
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# IAM Policy for Lambda to access DynamoDB
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_name}-lambda-policy-${var.environment}"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query"
        ]
        Resource = var.dynamodb_arns
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          "arn:aws:logs:*:*:log-group:/aws/lambda/${var.project_name}-handler-${var.environment}",
          "arn:aws:logs:*:*:log-group:/aws/lambda/${var.project_name}-handler-${var.environment}:*"
        ]
      }
    ]
  })
}

# Lambda Function for Chatbot
resource "aws_lambda_function" "chatbot_handler" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${var.project_name}-handler-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = var.handler
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = var.runtime
  timeout          = var.timeout
  memory_size      = var.memory_size

  environment {
    variables = {
      SESSIONS_TABLE   = var.sessions_table_name
      CUSTOMERS_TABLE  = var.customers_table_name
      ENVIRONMENT      = var.environment
      SESSION_TTL_HOURS = tostring(var.session_ttl_hours)
      ALLOWED_ORIGINS  = var.allowed_origins
    }
  }

  tags = {
    Name        = "${var.project_name}-handler"
    Environment = var.environment
  }
}
