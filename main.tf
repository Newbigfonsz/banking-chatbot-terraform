terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "BankingChatbot"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "DevOps Team"
    }
  }
}

# DynamoDB tables for chatbot data
module "dynamodb" {
  source      = "./modules/dynamodb"
  environment = var.environment
}

# Lambda functions for chatbot logic
module "lambda" {
  source = "./modules/lambda"

  project_name         = var.project_name
  environment          = var.environment
  sessions_table_name  = module.dynamodb.sessions_table_name
  customers_table_name = module.dynamodb.customers_table_name
  dynamodb_arns = [
    module.dynamodb.sessions_table_arn,
    module.dynamodb.customers_table_arn
  ]
}

# API Gateway for web access
module "api_gateway" {
  source = "./modules/api_gateway"

  project_name         = var.project_name
  environment          = var.environment
  lambda_function_arn  = module.lambda.lambda_function_arn
  lambda_function_name = module.lambda.lambda_function_name
}

# Outputs
output "dynamodb_tables" {
  value = {
    sessions_table  = module.dynamodb.sessions_table_name
    customers_table = module.dynamodb.customers_table_name
  }
  description = "DynamoDB table names"
}

output "lambda_function" {
  value = {
    name = module.lambda.lambda_function_name
    arn  = module.lambda.lambda_function_arn
  }
  description = "Lambda function details"
}

output "api_gateway_url" {
  value       = module.api_gateway.api_gateway_url
  description = "API Gateway URL for the chatbot"
}
