output "api_gateway_url" {
  value = "${aws_api_gateway_deployment.chatbot_deployment.invoke_url}/chat"
}

output "api_gateway_id" {
  value = aws_api_gateway_rest_api.chatbot_api.id
}
