import json
import boto3
from decimal import Decimal

# Custom JSON encoder to handle Decimal objects
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Inventory')

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))
    
    try:
        # Check if pathParameters exists and has 'id'
        if 'pathParameters' not in event or 'id' not in event['pathParameters']:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing item ID in URL path'})
            }
        
        # Get item_id from path parameters
        item_id = event['pathParameters']['id']
        print(f"Looking for item_id: {item_id}")
        
        # Use scan to find the item (since we don't have location_id)
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('item_id').eq(item_id)
        )
        
        print(f"Found {len(response['Items'])} items")
        
        if response['Items']:
            item = response['Items'][0]  # Get the first matching item
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(item, cls=DecimalEncoder)
            }
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Item not found'})
            }
            
    except Exception as e:
        print("Error occurred:", str(e))
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }