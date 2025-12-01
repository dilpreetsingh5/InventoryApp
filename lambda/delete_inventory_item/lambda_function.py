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
        # Get item_id from path parameters
        item_id = event['pathParameters']['id']
        print(f"Looking for item with item_id: {item_id}")
        
        # First, we need to find the item to get its location_id
        # We'll use a scan to find items with this item_id
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('item_id').eq(item_id)
        )
        
        print(f"Found {len(response['Items'])} items with item_id: {item_id}")
        
        if not response['Items']:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Item not found'})
            }
        
        # Get the first matching item
        item_to_delete = response['Items'][0]
        location_id = item_to_delete['location_id']
        
        print(f"Deleting item - item_id: {item_id}, location_id: {location_id}")
        
        # Now delete with both primary key components
        delete_response = table.delete_item(
            Key={
                'item_id': item_id,
                'location_id': location_id
            },
            ReturnValues='ALL_OLD'
        )
        
        print("Delete successful:", delete_response)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Item deleted successfully',
                'deleted_item': item_to_delete
            }, cls=DecimalEncoder)
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