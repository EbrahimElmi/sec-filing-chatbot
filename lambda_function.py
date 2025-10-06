import json
import boto3
from chatbot_service import SECChatbot
import config

# Initialize the chatbot service
chatbot = SECChatbot()

def lambda_handler(event, context):
    """
    AWS Lambda handler for the SEC Chatbot API.
    Handles HTTP requests and returns JSON responses.
    """
    
    # Set CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
    }
    
    try:
        # Handle preflight OPTIONS request
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'CORS preflight'})
            }
        
        # Parse the request
        if event.get('httpMethod') == 'GET':
            # Handle GET requests (health check, etc.)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'message': 'SEC Chatbot API is running',
                    'version': '1.0.0',
                    'endpoints': {
                        'POST /chat': 'Send chat messages',
                        'GET /health': 'Health check'
                    }
                })
            }
        
        elif event.get('httpMethod') == 'POST':
            # Parse request body
            try:
                if isinstance(event.get('body'), str):
                    body = json.loads(event['body'])
                else:
                    body = event.get('body', {})
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'Invalid JSON in request body'})
                }
            
            # Extract query and context
            user_query = body.get('query', '').strip()
            context = body.get('context', {})
            
            if not user_query:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'Query is required'})
                }
            
            # Process the query
            response = chatbot.process_query(user_query, context)
            
            # Return response
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(response)
            }
        
        else:
            return {
                'statusCode': 405,
                'headers': headers,
                'body': json.dumps({'error': 'Method not allowed'})
            }
    
    except Exception as e:
        # Log error (in production, use CloudWatch)
        print(f"Error in lambda_handler: {str(e)}")
        
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }

def health_check(event, context):
    """Health check endpoint for AWS Lambda."""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'status': 'healthy',
            'service': 'SEC Chatbot',
            'timestamp': context.aws_request_id if context else 'local'
        })
    }
