# Google Voice Text Application Setup

## Overview
This document outlines the steps performed in setting up the Google Voice Text Application project. The steps include creating a DynamoDB table, an EC2 instance with Ubuntu, and an S3 bucket. Currently, the project is at the point of cloning the repository.

## Steps Completed

### 1. Create DynamoDB Table: `googlevoicetext`
- **Log in to AWS Management Console**:
  1. Navigate to the AWS Management Console.
  2. Log in with your credentials.

- **Access DynamoDB**:
  1. In the services menu, find and click on **DynamoDB**.

- **Create Table**:
  1. Click on **Create table**.
  2. Enter the **Table name**: `googlevoicetext`.
  3. Set the **Primary key** (e.g., `id` of type String).
  4. Configure additional settings as necessary (e.g., provisioned read/write capacity).
  5. Click **Create** to finalize the creation of the table.

### 2. Create EC2 Instance: `google textapp`
- **Access EC2 Dashboard**:
  1. From the services menu, select **EC2**.

- **Launch Instance**:
  1. Click on **Launch instance**.
  2. Choose an **Amazon Machine Image (AMI)** (select **Ubuntu**).
  3. Select an **Instance Type** (e.g., t2.micro for free tier).
  4. Configure instance details, such as the number of instances and network settings (use a default VPC).
  5. Add **Storage** (default is usually sufficient).
  6. **Configure Security Group**:
     - Allow SSH access (port 22) from your IP.
     - Add any additional rules for your application (e.g., HTTP, HTTPS).
  7. Review your settings and click **Launch**.
  8. **Create or select a key pair** (e.g., `googletextapp.pem`) to access your instance.
  9. Click **Launch Instances** to finalize.

### 3. Create S3 Bucket: `google-voice-data`
- **Access S3 Dashboard**:
  1. From the services menu, select **S3**.

- **Create Bucket**:
  1. Click on **Create bucket**.
  2. Enter the **Bucket name**: `google-voice-data`.
  3. Choose a region (ensure it's the same region as your DynamoDB table and EC2 instance).
  4. Configure options such as versioning or logging as needed.
  5. Set permissions (public access settings should be configured based on your use case).
  6. Click **Create bucket** to finalize.

### 4. Connect to the EC2 Instance and Set Up Environment
- **Connect to the EC2 Instance**:
  1. Open a terminal or command prompt.
  2. Use the following command to SSH into your instance:
     ```bash
     ssh -i "DIRECTORY-OF-YOUR-PEM-FILE" ubuntu@<your-instance-public-ip>
     ```

- **Update the Server**:
  ```bash
  sudo apt update && sudo apt upgrade -y
