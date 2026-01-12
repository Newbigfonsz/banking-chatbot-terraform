output "lambda_function_arn" {
  value = aws_lambda_function.chatbot_handler.arn
}

output "lambda_function_name" {
  value = aws_lambda_function.chatbot_handler.function_name
}

output "lambda_role_arn" {
  value = aws_iam_role.lambda_role.arn
}
