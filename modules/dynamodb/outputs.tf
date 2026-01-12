output "sessions_table_name" {
  value = aws_dynamodb_table.chatbot_sessions.name
}

output "sessions_table_arn" {
  value = aws_dynamodb_table.chatbot_sessions.arn
}

output "customers_table_name" {
  value = aws_dynamodb_table.customer_data.name
}

output "customers_table_arn" {
  value = aws_dynamodb_table.customer_data.arn
}
