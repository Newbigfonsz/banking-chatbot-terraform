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

variable "handler" {
  description = "Lambda function handler"
  type        = string
  default     = "index.handler"
}

variable "runtime" {
  description = "Lambda runtime"
  type        = string
  default     = "python3.11"
}

variable "timeout" {
  description = "Lambda timeout in seconds"
  type        = number
  default     = 30
}

variable "memory_size" {
  description = "Lambda memory size in MB"
  type        = number
  default     = 256
}

variable "session_ttl_hours" {
  description = "Session TTL in hours"
  type        = number
  default     = 1
}

variable "allowed_origins" {
  description = "Allowed CORS origins"
  type        = string
  default     = "*"
}
