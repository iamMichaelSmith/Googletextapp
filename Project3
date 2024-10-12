import boto3
from botocore.exceptions import ClientError
from bs4 import BeautifulSoup
import logging
from datetime import datetime
from io import BytesIO
import os
 
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
 
# Initialize AWS services
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TextMessages')  # Your DynamoDB table name
 
# S3 bucket details
BUCKET_NAME = 'XXXXXXXXXXXXXXXXX'
PREFIX = ''  # Leave this empty if your files are in the root of the bucket
 
def process_message(log):
    """Extract and return message data from a BeautifulSoup object."""
    try:
        timestamp = log.find('abbr', class_='dt')['title']
        sender = log.find('cite', class_='sender vcard').find('a', class_='tel')
        phone_number = sender['href'].replace('tel:', '') if sender else "Unknown"
        return {
            'PhoneNumber': phone_number,
            'Timestamp': timestamp,
            'Message': message_text
        }
    except AttributeError as e:
        logger.error(f"Error processing message: {e}")
        return None
 
def insert_into_dynamodb(item):
    """Insert an item into DynamoDB table."""
    try:
        table.put_item(Item=item)
    except ClientError as e:
        logger.error(f"Error inserting into DynamoDB: {e}")
 
def process_file(file_content):
    """Process a single HTML file content and insert messages into DynamoDB."""
    try:
        soup = BeautifulSoup(file_content, 'html.parser')
        chat_logs = soup.find_all('div', class_='message')
 
        for log in chat_logs:
            item = process_message(log)
            if item:
                insert_into_dynamodb(item)
    except Exception as e:
        logger.error(f"Error processing file content: {e}")
 
# Function to parse category and received status
def parse_file_info(file_name):
    parts = file_name.split(" - ")
    number = parts[0]
    category = parts[1]
    date_str = parts[2].replace(".html", "").replace("_", ":")
 
    # Parse the category into Text or Phone
    if category == "Text":
        category_value = "Text"
        received_value = "True"
    elif category == "Received":
        category_value = "Phone"
        received_value = "True"
    elif category == "Missed":
        category_value = "Phone"
        received_value = "False"
    else:
        category_value = "Unknown"
        received_value = "Null"
 
    # Convert date to ISO format
    date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    date_iso = date_obj.isoformat()
 
    return [number, category_value, received_value, date_iso]
 
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
 
                    # The full key (path + file name)
                    full_key = obj['Key']
 
                    # Extract just the file name
                    file_name = os.path.basename(full_key)
                    print(file_name)
 
                    #[number, category_value, received_value, date_iso]
                    data = parse_file_info(file_name)
 
                    # Will this work?
                    insert_into_dynamodb(data)
 
 
                    # file_content = file_obj['Body'].read()
 
                    # # Process the file content
                    # process_file(file_content)
 
    except Exception as e:
        logger.error(f"Error processing S3 bucket: {e}")
 
    end_time = datetime.now()
    logger.info(f"Finished processing at {end_time}")
    logger.info(f"Total processing time: {end_time - start_time}")
 
if __name__ == "__main__":
    main()
