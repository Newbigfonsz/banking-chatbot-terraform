variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "sessions_table_name" {
  description = "DynamoDB sessions table name"
  type        = string
}

variable "customers_table_name" {
  description = "DynamoDB customers table name"
  type        = string
}

variable "dynamodb_arns" {
  description = "List of DynamoDB table ARNs"
  type        = list(string)
}
