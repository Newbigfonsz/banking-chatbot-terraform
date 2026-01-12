import json
import boto3
import os
from datetime import datetime

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
sessions_table = dynamodb.Table(os.environ['SESSIONS_TABLE'])
customers_table = dynamodb.Table(os.environ['CUSTOMERS_TABLE'])

def handler(event, context):
    """
    Main handler for the banking chatbot
    """
    print(f"Received event: {json.dumps(event)}")
    
    # Parse the body if it's a string
    if isinstance(event.get('body'), str):
        try:
            body = json.loads(event['body'])
        except:
            body = {}
    else:
        body = event.get('body', {})
    
    # Extract message from body
    message = body.get('message', '')
    session_id = body.get('sessionId', 'default')
    
    # Simple response logic
    if 'balance' in message.lower():
        response_text = "Your current balance is $5,432.10"
    elif 'transfer' in message.lower():
        response_text = "To transfer funds, please specify the amount and destination account."
    elif 'help' in message.lower():
        response_text = "I can help you with: checking balance, transfers, transaction history, and account settings."
    else:
        response_text = f"Hello! I'm your banking assistant. You said: {message}"
    
    # Store session data
    try:
        sessions_table.put_item(
            Item={
                'sessionId': session_id,
                'timestamp': datetime.utcnow().isoformat(),
                'message': message,
                'response': response_text,
                'ttl': int(datetime.utcnow().timestamp()) + 3600  # Expire after 1 hour
            }
        )
    except Exception as e:
        print(f"Error storing session: {str(e)}")
    
    # Return with CORS headers
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps({
            'response': response_text,
            'sessionId': session_id,
            'timestamp': datetime.utcnow().isoformat()
        })
    }
