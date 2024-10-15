import json
import os
import boto3
from botocore.exceptions import ClientError
import requests
import random
import feedparser
import logging
from datetime import datetime
from boto3.dynamodb.conditions import Attr
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# S3 bucket details
BUCKET_NAME = 'google-voice-data'
REGION_NAME = 'us-east-1'  # Replace with your actual region if different
PREFIX = ''  # Leave this empty if your files are in the root of the bucket

# Initialize AWS services
try:
    session = boto3.Session(region_name=REGION_NAME)
    s3 = session.client('s3')
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table('googlevoicetext')  # Your DynamoDB table name

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
        all_objects = []
        paginator = s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix=PREFIX):
            if 'Contents' in page:
                all_objects.extend(page['Contents'])
        logger.info(f"Found {len(all_objects)} objects in the bucket.")
        return all_objects
    except ClientError as e:
        logger.error(f"Error listing objects in bucket {BUCKET_NAME}: {e}")
        return None

def extract_info_from_html(html_content, key):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract phone number from filename
    phone_number = key.split(' - ')[0].strip('+')
    
    # Extract timestamp
    timestamp_elem = soup.find('div', class_='timestamp')
    timestamp = timestamp_elem.text.strip() if timestamp_elem else None
    
    # Extract message or duration
    message_elem = soup.find('div', class_='message-content')
    duration_elem = soup.find('div', class_='duration')
    
    if message_elem:
        content = message_elem.text.strip()
        call_type = 'Text'
    elif duration_elem:
        content = duration_elem.text.strip()
        call_type = 'Call'
    else:
        content = None
        call_type = 'Unknown'
    
    return {
        'PhoneNumber': phone_number,
        'Timestamp': timestamp,
        'Content': content,
        'Type': call_type
    }

def process_file(key):
    """Process a single file from S3."""
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        content_type = response['ContentType']
        file_content = response['Body'].read().decode('utf-8')

        if 'json' in content_type:
            data = json.loads(file_content)
        elif 'html' in content_type:
            data = extract_info_from_html(file_content, key)
        else:
            logger.warning(f"Skipping unsupported file type: {key}")
            return False

        # Check if the phone number already exists
        phone_number = data.get('PhoneNumber')
        if phone_number:
            existing_item = table.get_item(Key={'PhoneNumber': phone_number})
            if 'Item' not in existing_item:
                # Phone number doesn't exist, insert the new item
                table.put_item(Item=data)
                logger.info(f"Inserted new item for phone number: {phone_number}")
                return True
            else:
                logger.info(f"Skipped duplicate phone number: {phone_number}")
        else:
            logger.warning(f"Skipping file {key}: No PhoneNumber found in data")

    except UnicodeDecodeError:
        logger.warning(f"Skipping file {key}: Not a UTF-8 encoded file")
    except json.JSONDecodeError:
        logger.warning(f"Skipping file {key}: Not a valid JSON file")
    except ClientError as e:
        logger.warning(f"Error accessing file {key}: {e}")
    except Exception as e:
        logger.warning(f"Unexpected error processing file {key}: {e}")
    
    return False

def main():
    logger.info(f"Starting processing at {datetime.now()}")
    
    try:
        s3_objects = list_s3_objects()
        if s3_objects:
            total_files = len(s3_objects)
            successful_imports = 0
            for obj in s3_objects:
                if process_file(obj['Key']):
                    successful_imports += 1
                if successful_imports % 100 == 0 and successful_imports > 0:
                    logger.info(f"Processed {successful_imports} files so far...")
            
            logger.info(f"Processing complete. Successfully imported {successful_imports} out of {total_files} files.")
        else:
            logger.warning("No objects found in the S3 bucket or error occurred.")
    except Exception as e:
        logger.error(f"Error processing S3 bucket: {e}")
    
    logger.info(f"Finished processing at {datetime.now()}")

if __name__ == "__main__":
    main()
