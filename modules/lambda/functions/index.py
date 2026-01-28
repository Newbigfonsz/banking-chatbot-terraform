import json
import logging
import os
import uuid
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

# Configure structured logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variable validation
REQUIRED_ENV_VARS = ['SESSIONS_TABLE', 'CUSTOMERS_TABLE']
for var in REQUIRED_ENV_VARS:
    if var not in os.environ:
        logger.error(f"Missing required environment variable: {var}")
        raise EnvironmentError(f"Missing required environment variable: {var}")

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
sessions_table = dynamodb.Table(os.environ['SESSIONS_TABLE'])
customers_table = dynamodb.Table(os.environ['CUSTOMERS_TABLE'])

# Configuration from environment
SESSION_TTL_HOURS = int(os.environ.get('SESSION_TTL_HOURS', '1'))
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '*')
MAX_MESSAGE_LENGTH = 1000


def get_cors_headers():
    """Return CORS headers for the response."""
    return {
        'Access-Control-Allow-Origin': ALLOWED_ORIGINS,
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    }


def validate_session_id(session_id):
    """Validate session ID format."""
    if not session_id or not isinstance(session_id, str):
        return False
    if len(session_id) > 100:
        return False
    return True


def validate_message(message):
    """Validate message input."""
    if not isinstance(message, str):
        return False, "Message must be a string"
    if len(message) > MAX_MESSAGE_LENGTH:
        return False, f"Message exceeds maximum length of {MAX_MESSAGE_LENGTH} characters"
    return True, None


def generate_response(message):
    """Generate chatbot response based on message content."""
    message_lower = message.lower()

    if 'balance' in message_lower:
        return "Your current balance is $5,432.10"
    elif 'transfer' in message_lower:
        return "To transfer funds, please specify the amount and destination account."
    elif 'help' in message_lower:
        return "I can help you with: checking balance, transfers, transaction history, and account settings."
    else:
        return f"Hello! I'm your banking assistant. You said: {message}"


def store_session(session_id, message, response_text):
    """Store session data in DynamoDB."""
    try:
        ttl_seconds = SESSION_TTL_HOURS * 3600
        sessions_table.put_item(
            Item={
                'sessionId': session_id,
                'timestamp': datetime.utcnow().isoformat(),
                'message': message,
                'response': response_text,
                'ttl': int(datetime.utcnow().timestamp()) + ttl_seconds
            }
        )
        return True
    except ClientError as e:
        logger.error(f"Error storing session: {e.response['Error']['Message']}")
        return False


def create_response(status_code, body):
    """Create a standardized API response."""
    return {
        'statusCode': status_code,
        'headers': get_cors_headers(),
        'body': json.dumps(body)
    }


def handler(event, context):
    """
    Main handler for the banking chatbot.

    Args:
        event: API Gateway event containing the request
        context: Lambda context object

    Returns:
        dict: API Gateway response with status code, headers, and body
    """
    request_id = context.aws_request_id if context else str(uuid.uuid4())
    logger.info(f"Request ID: {request_id} - Processing request")

    # Parse the body
    body = {}
    if isinstance(event.get('body'), str):
        try:
            body = json.loads(event['body'])
        except json.JSONDecodeError as e:
            logger.warning(f"Request ID: {request_id} - Invalid JSON in request body: {e}")
            return create_response(400, {'error': 'Invalid JSON in request body'})
        except TypeError as e:
            logger.warning(f"Request ID: {request_id} - Type error parsing body: {e}")
            return create_response(400, {'error': 'Invalid request body'})
    elif isinstance(event.get('body'), dict):
        body = event.get('body', {})

    # Extract and validate message
    message = body.get('message', '')
    is_valid, error_message = validate_message(message)
    if not is_valid:
        logger.warning(f"Request ID: {request_id} - Invalid message: {error_message}")
        return create_response(400, {'error': error_message})

    # Extract and validate session ID
    session_id = body.get('sessionId', str(uuid.uuid4()))
    if not validate_session_id(session_id):
        logger.warning(f"Request ID: {request_id} - Invalid session ID format")
        return create_response(400, {'error': 'Invalid session ID format'})

    # Generate response
    response_text = generate_response(message)

    # Store session data
    store_session(session_id, message, response_text)

    logger.info(f"Request ID: {request_id} - Successfully processed message for session: {session_id[:8]}...")

    return create_response(200, {
        'response': response_text,
        'sessionId': session_id,
        'timestamp': datetime.utcnow().isoformat()
    })
