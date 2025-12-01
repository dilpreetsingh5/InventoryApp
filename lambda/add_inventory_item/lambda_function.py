import json
import boto3
import uuid
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
    try:
        # Parse the request body
        body = json.loads(event['body'])
        
        # Generate a unique UUID for the new item
        new_item_id = str(uuid.uuid4())
        
        # Create the new item - using Decimal for numbers instead of float/int
        new_item = {
            'item_id': new_item_id,
            'item_name': body['item_name'],
            'item_description': body['item_description'],
            'item_qty_on_hand': Decimal(str(body['item_qty_on_hand'])),
            'item_price': Decimal(str(body['item_price'])),
            'location_id': Decimal(str(body['location_id']))
        }
        
        # Put the item in the table
        table.put_item(Item=new_item)
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Item added successfully',
                'item_id': new_item_id
            }, cls=DecimalEncoder)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }