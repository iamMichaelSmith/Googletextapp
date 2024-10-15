import boto3
from botocore.exceptions import ClientError
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Specify your AWS region here
REGION_NAME = 'us-east-1'  # Your region

# Initialize AWS services with the specified region
s3 = boto3.client('s3', region_name=REGION_NAME)
dynamodb = boto3.resource('dynamodb', region_name=REGION_NAME)
table = dynamodb.Table('TextMessages')  # Your DynamoDB table name

# S3 bucket details
BUCKET_NAME = 'google-voice-data'  # Your actual bucket name
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
            'Message': message_text,  # Include the message
            'Type': 'Text'            # Include the type as 'Text'
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
            'Type': 'Received Call'   # Include the type as 'Received Call'
        }
    except AttributeError as e:
        logger.error(f"Error processing call log: {e}")
        return None

def insert_into_dynamodb(item):
    """Insert an item into DynamoDB table."""
    try:
        table.put_item(Item=item)
        logger.info(f"Inserted item: {item}")  # Log the inserted item
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
        
        # Determine if it's a Text or Call log
        if category == "Text":
            category_value = "Text"
            received_value = "True"
        elif category == "Received":
            category_value = "Call"
            received_value = "True"
        elif category == "Missed":
            category_value = "Call"
            received_value = "False"
        else:
            category_value = "Unknown"
            received_value = "Null"
    
        # Convert date to ISO format
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        date_iso = date_obj.isoformat()

        return {
            'PhoneNumber': number,
            'Category': category_value,
            'Received': received_value,
            'Timestamp': date_iso
        }
    except Exception as e:
        logger.error(f"Error parsing file name: {e}")
        return None

def main():
    """Main function to process all HTML files in the S3 bucket."""
    start_time = datetime.now()
    logger.info(f"Starting processing at {start_time}")

    try:
        # List objects in the S3 bucket
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=BUCKET_NAME, Prefix=PREFIX)

        for page in pages:
            for obj in page.get('Contents', []):
                if obj['Key'].endswith('.html'):
                    logger.info(f"Processing file: {obj['Key']}")
                    # Get the file content
                    file_obj = s3.get_object(Bucket=BUCKET_NAME, Key=obj['Key'])
                    file_content = file_obj['Body'].read()

                    # Extract just the file name
                    file_name = os.path.basename(obj['Key'])
                    logger.info(f"File name: {file_name}")

                    # Parse the file name for categorization and timestamps
                    data = parse_file_info(file_name)

                    if data and data['Category'] == 'Text':
                        process_file(file_content, 'Text')
                    elif data and data['Category'] == 'Call':
                        process_file(file_content, 'Call')
    except Exception as e:
        logger.error(f"Error processing S3 bucket: {e}")

    end_time = datetime.now()
    logger.info(f"Finished processing at {end_time}")
    logger.info(f"Total processing time: {end_time - start_time}")

if __name__ == "__main__":
    main()
