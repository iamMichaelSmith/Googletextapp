import boto3
from botocore.exceptions import ClientError
from bs4 import BeautifulSoup
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Specify your AWS region here
REGION_NAME = 'us-east-1'  # Ensure this is your bucket's region

# Initialize AWS services with the specified region
s3 = boto3.client('s3', region_name=REGION_NAME)
dynamodb = boto3.resource('dynamodb', region_name=REGION_NAME)
table = dynamodb.Table('googlevoicetext')  # Your DynamoDB table name

# S3 bucket details
BUCKET_NAME = 'newgoogledatabucket'  # Ensure this matches the actual bucket name
PREFIX = ''  # Leave this empty if your files are in the root of the bucket

def process_message(log):
    """Extract and return message data from a BeautifulSoup object."""
    try:
        timestamp = log.find('abbr', class_='dt')['title']
        sender = log.find('cite', class_='sender vcard').find('a', class_='tel')
        phone_number = sender['href'].replace('tel:', '') if sender else "Unknown"
        message_text = log.find('q').get_text() if log.find('q') else "No message"
        return {
            'PhoneNumber': phone_number,
            'Timestamp': timestamp,
            'Message': message_text,
            'Type': 'Text'
        }
    except AttributeError as e:
        logger.error(f"Error processing message: {e}")
        return None

def process_call_log(log):
    """Extract and return call log data from a BeautifulSoup object."""
    try:
        timestamp = log.find('abbr', class_='published')['title']
        phone_number = log.find('a', class_='tel')['href'].replace('tel:', '')
        duration = log.find('abbr', class_='duration').get_text() if log.find('abbr', class_='duration') else "Unknown"
        return {
            'PhoneNumber': phone_number,
            'Timestamp': timestamp,
            'Duration': duration,
            'Type': 'Received Call'
        }
    except AttributeError as e:
        logger.error(f"Error processing call log: {e}")
        return None

def insert_into_dynamodb(item):
    """Insert an item into DynamoDB table."""
    try:
        table.put_item(Item=item)
        logger.info(f"Inserted item: {item}")
    except ClientError as e:
        logger.error(f"Error inserting into DynamoDB: {e.response['Error']['Message']}")

def process_file(file_content, category):
    """Process a single HTML file content and insert messages or calls into DynamoDB."""
    try:
        soup = BeautifulSoup(file_content, 'html.parser')

        if category == "Text":
            chat_logs = soup.find_all('div', class_='message')
            for log in chat_logs:
                item = process_message(log)
                if item:
                    insert_into_dynamodb(item)
        elif category == "Call":
            call_logs = soup.find_all('div', class_='haudio')
            for log in call_logs:
                item = process_call_log(log)
                if item:
                    insert_into_dynamodb(item)
    except Exception as e:
        logger.error(f"Error processing file content: {e}")

def parse_file_info(file_name):
    """Parse the file name to extract phone number, category, and timestamp."""
    try:
        parts = file_name.split(" - ")
        if len(parts) != 3:
            logger.error(f"Unexpected file name format: {file_name}")
            return None

        number = parts[0]
        category = parts[1]
        date_str = parts[2].replace(".html", "").replace("_", ":")
        
        if category == "Text":
            category_value = "Text"
        elif category in ["Received", "Missed"]:
            category_value = "Call"
        else:
            logger.error(f"Unknown category in file name: {file_name}")
            return None

        return {
            'number': number,
            'category': category_value,
            'date': date_str
        }
    except Exception as e:
        logger.error(f"Error parsing file info: {e}")
        return None

def list_all_s3_objects():
    """List all objects in the S3 bucket with pagination."""
    logger.info(f"Listing objects in bucket: {BUCKET_NAME}")  # Debug log for bucket name
    continuation_token = None
    all_objects = []

    try:
        while True:
            if continuation_token:
                response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PREFIX, ContinuationToken=continuation_token)
            else:
                response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PREFIX)

            if 'Contents' in response:
                all_objects.extend(response['Contents'])
                logger.info(f"Retrieved {len(response['Contents'])} objects.")  # Log number of objects retrieved
            
            # Check if there are more objects to retrieve
            if response.get('IsTruncated'):  # If response is truncated
                continuation_token = response.get('NextContinuationToken')
            else:
                break  # Exit the loop if no more objects

    except ClientError as e:
        logger.error(f"Error listing objects: {e}")

    return all_objects

def check_aws_identity():
    """Check and log the current AWS identity."""
    sts = boto3.client('sts', region_name=REGION_NAME)
    try:
        identity = sts.get_caller_identity()
        logger.info(f"Using AWS identity: {identity['Arn']}")
    except ClientError as e:
        logger.error(f"Error getting caller identity: {e}")

def main():
    logger.info("Starting processing at %s", datetime.now())
    check_aws_identity()
    
    try:
        s3_objects = list_all_s3_objects()
        if s3_objects:
            for obj in s3_objects:
                file_name = obj['Key']
                file_info = parse_file_info(file_name)
                if file_info:
                    response = s3.get_object(Bucket=BUCKET_NAME, Key=file_name)
                    file_content = response['Body'].read().decode('utf-8')
                    process_file(file_content, file_info['category'])
        else:
            logger.info("No objects found in the S3 bucket.")
    except ClientError as e:
        logger.error(f"Error processing S3 bucket: {e}")
    
    logger.info("Finished processing at %s", datetime.now())

if __name__ == "__main__":
    main()
