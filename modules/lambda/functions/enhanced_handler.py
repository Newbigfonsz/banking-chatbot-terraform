import json
import boto3
import os
from datetime import datetime, timedelta
import random
import re

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
sessions_table = dynamodb.Table(os.environ['SESSIONS_TABLE'])
customers_table = dynamodb.Table(os.environ['CUSTOMERS_TABLE'])

# Sample data for demo
SAMPLE_ACCOUNTS = {
    "checking": {
        "balance": 5432.10,
        "number": "****1234",
        "type": "Premium Checking"
    },
    "savings": {
        "balance": 15750.25,
        "number": "****5678",
        "type": "High-Yield Savings"
    },
    "credit": {
        "balance": -2340.50,
        "available": 7659.50,
        "number": "****9012",
        "type": "Rewards Card"
    }
}

RECENT_TRANSACTIONS = [
    {"date": "Today", "desc": "Starbucks Coffee", "amount": -5.85, "balance": 5432.10},
    {"date": "Yesterday", "desc": "Direct Deposit - Salary", "amount": 3500.00, "balance": 5437.95},
    {"date": "Jan 13", "desc": "Amazon Purchase", "amount": -67.42, "balance": 1937.95},
    {"date": "Jan 12", "desc": "Transfer from Savings", "amount": 500.00, "balance": 2005.37},
    {"date": "Jan 11", "desc": "Walmart Grocery", "amount": -142.38, "balance": 1505.37}
]

ATM_LOCATIONS = [
    "📍 SecureBank ATM - 123 Main St (0.3 miles)",
    "📍 Partner ATM - Walmart, 456 Oak Ave (0.8 miles)",
    "📍 SecureBank Branch - 789 Pine Rd (1.2 miles)",
    "📍 Partner ATM - 7-Eleven, 321 Elm St (1.5 miles)"
]

def parse_amount(text):
    """Extract dollar amount from text"""
    match = re.search(r'\$?(\d+(?:\.\d{2})?)', text)
    if match:
        return float(match.group(1))
    return None

def get_conversation_state(session_id):
    """Get current conversation state from DynamoDB"""
    try:
        response = sessions_table.get_item(Key={'sessionId': session_id})
        if 'Item' in response:
            return response['Item'].get('conversationState', {})
    except:
        pass
    return {}

def save_conversation_state(session_id, state):
    """Save conversation state to DynamoDB"""
    try:
        sessions_table.update_item(
            Key={'sessionId': session_id},
            UpdateExpression="SET conversationState = :state",
            ExpressionAttributeValues={':state': state}
        )
    except:
        pass

def format_currency(amount):
    """Format number as currency"""
    return f"${amount:,.2f}"

def handler(event, context):
    """Enhanced banking chatbot handler"""
    print(f"Received event: {json.dumps(event)}")
    
    # Parse the body if it's a string (from API Gateway)
    if isinstance(event.get('body'), str):
        try:
            body = json.loads(event['body'])
        except:
            body = {}
    else:
        body = event.get('body', {})
    
    # Extract message and session
    message = body.get('message', '').lower()
    session_id = body.get('sessionId', 'default')
    
    # Get conversation state
    state = get_conversation_state(session_id)
    
    # Initialize response
    response_text = ""
    
    # Check for conversation flows
    if state.get('pending_action') == 'transfer_amount':
        # User is in middle of transfer flow
        amount = parse_amount(message)
        if amount:
            if amount > SAMPLE_ACCOUNTS['checking']['balance']:
                response_text = f"❌ Insufficient funds. Your checking balance is {format_currency(SAMPLE_ACCOUNTS['checking']['balance'])}. Please enter a smaller amount or type 'cancel' to stop."
            else:
                state['transfer_amount'] = amount
                state['pending_action'] = 'transfer_confirm'
                response_text = f"💸 Ready to transfer {format_currency(amount)} from Checking {SAMPLE_ACCOUNTS['checking']['number']} to Savings {SAMPLE_ACCOUNTS['savings']['number']}.\n\n⚠️ Please type 'confirm' to proceed or 'cancel' to stop."
        else:
            response_text = "Please enter a valid amount (e.g., $100 or 100)"
    
    elif state.get('pending_action') == 'transfer_confirm':
        if 'confirm' in message:
            amount = state.get('transfer_amount', 0)
            new_checking = SAMPLE_ACCOUNTS['checking']['balance'] - amount
            new_savings = SAMPLE_ACCOUNTS['savings']['balance'] + amount
            response_text = f"""✅ Transfer Successful!

📤 From: Checking {SAMPLE_ACCOUNTS['checking']['number']}
📥 To: Savings {SAMPLE_ACCOUNTS['savings']['number']}
💵 Amount: {format_currency(amount)}
🔢 Confirmation: #{random.randint(100000, 999999)}

New Balances:
- Checking: {format_currency(new_checking)}
- Savings: {format_currency(new_savings)}"""
            state = {}  # Clear state
        elif 'cancel' in message:
            response_text = "Transfer cancelled. How else can I help you?"
            state = {}
        else:
            response_text = "Please type 'confirm' to complete the transfer or 'cancel' to stop."
    
    # Standard responses for common queries
    elif 'balance' in message or 'how much' in message:
        if 'savings' in message:
            response_text = f"💰 Savings Account {SAMPLE_ACCOUNTS['savings']['number']}\nBalance: {format_currency(SAMPLE_ACCOUNTS['savings']['balance'])}\n\nInterest earned this month: $47.25"
        elif 'credit' in message:
            response_text = f"💳 Credit Card {SAMPLE_ACCOUNTS['credit']['number']}\nCurrent Balance: {format_currency(-SAMPLE_ACCOUNTS['credit']['balance'])}\nAvailable Credit: {format_currency(SAMPLE_ACCOUNTS['credit']['available'])}\nMinimum Payment Due: $35.00"
        else:
            response_text = f"""💰 Your Account Balances:

🏦 Checking {SAMPLE_ACCOUNTS['checking']['number']}
   Balance: {format_currency(SAMPLE_ACCOUNTS['checking']['balance'])}
   
💎 Savings {SAMPLE_ACCOUNTS['savings']['number']}
   Balance: {format_currency(SAMPLE_ACCOUNTS['savings']['balance'])}
   
💳 Credit Card {SAMPLE_ACCOUNTS['credit']['number']}
   Balance: {format_currency(-SAMPLE_ACCOUNTS['credit']['balance'])}
   Available: {format_currency(SAMPLE_ACCOUNTS['credit']['available'])}"""
    
    elif 'transaction' in message or 'recent' in message or 'history' in message:
        trans_list = "\n".join([
            f"• {t['date']}: {t['desc']} {'(+' if t['amount'] > 0 else ''}{format_currency(abs(t['amount']))}{')'}"
            for t in RECENT_TRANSACTIONS[:5]
        ])
        response_text = f"📊 Recent Transactions (Checking):\n\n{trans_list}\n\nCurrent Balance: {format_currency(SAMPLE_ACCOUNTS['checking']['balance'])}"
    
    elif 'transfer' in message:
        state = {'pending_action': 'transfer_amount'}
        response_text = "💸 Let's set up your transfer.\n\nHow much would you like to transfer from Checking to Savings?\n\n(Enter amount like $100 or just 100)"
    
    elif 'atm' in message or 'branch' in message:
        locations = "\n".join(ATM_LOCATIONS)
        response_text = f"📍 Nearest ATM Locations:\n\n{locations}\n\n💡 Tip: SecureBank ATMs have no fees. Partner ATMs may charge $3.00"
    
    elif 'pay' in message or 'bill' in message:
        response_text = """💳 Upcoming Bills:

- Electricity - $142.50 (Due Jan 20)
- Internet - $79.99 (Due Jan 22)
- Credit Card - $35.00 (Min. payment due Jan 25)
- Netflix - $15.99 (Auto-pay Jan 28)

Would you like to pay any of these bills now?"""
    
    elif 'help' in message:
        response_text = """🤝 I can help you with:

💰 Check balances - "What's my balance?"
📊 View transactions - "Show recent transactions"
💸 Transfer money - "Transfer funds"
📍 Find ATMs - "Where's the nearest ATM?"
💳 Pay bills - "Show my bills"
📞 Support - "Talk to support"
🔐 Security - "Is my account secure?"

Just type or click any quick action button above!"""
    
    elif 'hello' in message or 'hi' in message:
        hour = datetime.now().hour
        greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
        response_text = f"{greeting}! 👋 Welcome to SecureBank. How can I assist you today?"
    
    elif 'thank' in message:
        response_text = "You're welcome! 😊 Is there anything else I can help you with today?"
    
    elif 'secure' in message or 'safe' in message or 'security' in message:
        response_text = """🔐 Your Security Status:

✅ 256-bit encryption active
✅ Two-factor authentication enabled
✅ Last login: Today at 2:15 PM from this device
✅ No suspicious activity detected

Your account is fully protected. If you notice anything unusual, type 'report fraud' immediately."""
    
    else:
        # Default response with suggestions
        response_text = f"I'd be happy to help! You said: '{body.get('message', '')}'\n\nTry asking about:\n• Account balance\n• Recent transactions\n• Transfer money\n• Find ATM\n\nOr click the quick action buttons above!"
    
    # Save updated state
    if state != get_conversation_state(session_id):
        save_conversation_state(session_id, state)
    
    # Store session data
    try:
        sessions_table.put_item(
            Item={
                'sessionId': session_id,
                'timestamp': datetime.utcnow().isoformat(),
                'message': body.get('message', ''),
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
