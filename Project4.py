import json
import os
import boto3
from botocore.exceptions import ClientError
import requests
import random
import feedparser
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# S3 bucket details
BUCKET_NAME = 'XXXXXXXvoice-data'  # Make sure this is correct
REGION_NAME = 'us-east-1'  # Replace with your actual region if different
PREFIX = ''  # Leave this empty if your files are in the root of the bucket

# Initialize AWS services
try:
    session = boto3.Session(region_name=REGION_NAME)
    s3 = session.client('s3')
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table('DiscordBotData')  # Your DynamoDB table name

    # Verify credentials
    credentials = session.get_credentials()
    logger.info(f"Access Key ID being used: {credentials.access_key[:5]}...")

    # Check AWS identity
    sts = session.client('sts')
    identity = sts.get_caller_identity()
    logger.info(f"Using AWS identity: {identity['Arn']}")

except Exception as e:
    logger.error(f"Error initializing AWS services: {e}")
    raise

def list_s3_objects():
    """List objects in the S3 bucket."""
    try:
        logger.info(f"Attempting to list objects in bucket: {BUCKET_NAME}")
        logger.info(f"Using region: {REGION_NAME}")
        logger.info(f"S3 client: {s3}")
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PREFIX)
        logger.info(f"Response: {response}")
        return response.get('Contents', [])
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"Error listing objects in bucket {BUCKET_NAME}. Error Code: {error_code}, Message: {error_message}")
        if error_code == 'NoSuchBucket':
            logger.error(f"The bucket {BUCKET_NAME} does not exist or you don't have permission to access it.")
        elif error_code == 'AccessDenied':
            logger.error(f"Access denied to bucket {BUCKET_NAME}. Check your permissions.")
        return None

def get_random_media(bucket_name):
    """Get a random media file from S3."""
    objects = list_s3_objects()
    if objects:
        random_object = random.choice(objects)
        return f"https://{bucket_name}.s3.amazonaws.com/{random_object['Key']}"
    return None

def fetch_hiphop_news():
    """Fetch hip-hop news from RSS feed."""
    rss_url = 'https://www.xxlmag.com/rss'  # Example RSS feed URL
    try:
        feed = feedparser.parse(rss_url)
        articles = []
        for entry in feed.entries[:5]:  # Get the latest 5 articles
            articles.append({
                'title': entry.title,
                'link': entry.link
            })
        return articles
    except Exception as e:
        logger.error(f"Error fetching hip-hop news: {e}")
        return []

def lambda_handler(event, context):
    """Lambda function handler."""
    logger.info(f"Event received: {event}")
    command = event.get('command', '')

    if command == '/media':
        media_url = get_random_media(BUCKET_NAME)
        if media_url:
            return {
                'statusCode': 200,
                'body': json.dumps({'media_url': media_url})
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'No media files found!'})
            }
    
    elif command == '/news':
        news_articles = fetch_hiphop_news()
        return {
            'statusCode': 200,
            'body': json.dumps({'articles': news_articles})
        }

    elif command.startswith('/info'):
        user_id = event.get('user_id')
        try:
            table.put_item(Item={'UserId': user_id, 'Interaction': command})
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Your interaction has been recorded!'})
            }
        except Exception as e:
            logger.error(f"Error recording interaction: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'Error recording interaction'})
            }

    return {
        'statusCode': 400,
        'body': json.dumps({'message': 'Unknown command!'})
    }

def main():
    logger.info(f"Starting processing at {datetime.now()}")
    logger.info(f"Using bucket name: {BUCKET_NAME}")
    logger.info(f"Using region: {REGION_NAME}")

    try:
        s3_objects = list_s3_objects()
        if s3_objects:
            logger.info(f"Successfully listed {len(s3_objects)} objects in the S3 bucket.")
            # Process your objects here
        else:
            logger.warning("No objects found in the S3 bucket or error occurred.")
    except Exception as e:
        logger.error(f"Error processing S3 bucket: {e}")
    
    logger.info(f"Finished processing at {datetime.now()}")

if __name__ == "__main__":
    main()
