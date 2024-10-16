<a href="https://ibb.co/tQ5WmKh"><img src="https://i.ibb.co/ckd7g3v/Dynamo-DB-Table-Creation-Google-text-app-Diagram.png" alt="Dynamo-DB-Table-Creation-Google-text-app-Diagram" border="0"></a>
# Google Voice Text Application Setup

## Overview
This document outlines the steps I have performed so far in setting up the Google Voice Text Application project. The steps include creating a DynamoDB table, an EC2 instance with Ubuntu, and an S3 bucket. Currently, I am at the point of cloning the repository.

## Google Takeout Overview

**Google Takeout** is a service provided by Google that allows users to export and download their data from various Google services in a convenient and organized manner. This feature is especially useful for users who want to back up their information or migrate it to another platform. 

### Functionality of Google Takeout for Google Voice

When it comes to **Google Voice**, Google Takeout enables users to download a comprehensive archive of their voice calls and text message data. The exported data typically includes:

- **Voice Calls**: Detailed logs of all incoming and outgoing calls, including timestamps, durations, and the phone numbers involved.
- **Text Messages**: A record of SMS and MMS conversations, along with timestamps and sender/receiver information.
- **Voicemail Messages**: Audio files of voicemail messages left by callers.

### Usage in Projects

For projects that involve data processing or analysis of communication patterns, accessing Google Voice data through Google Takeout provides a structured format that can be easily imported into databases or analytical tools. This allows developers and researchers to leverage this data for various applications, such as building chatbots, analyzing user interactions, or developing insights into communication habits.

## Steps Completed

### 1. Create DynamoDB Table: `googlevoicetext`
- **Log in to AWS Management Console**:
  1. Navigate to the [AWS Management Console](https://aws.amazon.com/console/).
  2. Log in with your credentials.

- **Access DynamoDB**:
  1. In the services menu, find and click on **DynamoDB**.

- **Create Table**:
  1. Click on **Create table**.
  2. Enter the **Table name**: `googlevoicetext`.
  3. Set the **Primary key** String > PhoneNumber.
  4. Set the **Sort Key key** String > Time Stamp.
  5. Configure additional settings as necessary (e.g., provisioned read/write capacity).
  6. Click **Create** to finalize the creation of the table.
  7. Once Done, Click on "googlevoicetext" table and click "Explore table items"
  8. Select "Create item" and then "Add new attribute"
  9. Add "String > Message, String > Type. This will allow you to parse these attributes to DynamoDB.
  10. Save.

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
  7. Review your settings and click **Launch**.
  8. **Create or select a key pair** (e.g., `googletextapp.pem`) to access your instance.
  9. Click **Launch Instances** to finalize.
  10. Create IAM Role for EC2 to have full access to Dynamo DB and S3


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
  7. Upload Google Takeout (Calls) data to the S3 bucket.
  8. Set bucket permission to allow "ListBucket & GetObject"
  

- **Connect to the EC2 Instance**:
  1. Open a terminal or command prompt.
  2. Use the following command to SSH into your instance:
    ```bash
    ssh -i "YOUR-DIRECTORY-OF-YOUR-PEM-FILE" ubuntu@<your-instance-public-ip>
    ```

- **Update & Upgrade the instance**:
   3. Use the following command to update & upgrade your instance:
  ```bash
  sudo apt update && sudo apt upgrade -y
  ```

- **activate virtual enviroment on your instance**:
  4. Use the following command to activate virtual enviroment on your instance:
    ```bash
  source ~/awsenv/bin/activate
    ```

 - **Install latest version of Nodejs**:
    4. Use the following command to install Nodejs to your instance:
      ```bash
      sudo apt install -y nodejs
      ```
      
 - **Install latest version of Install Boto3**:
    5. Use the following command to install Install Boto3 to your instance:
      ```bash
      pip install boto3
      ```

 - **Install latest version of Python**:
    6. Use the following command to install Python to your instance:
      ```bash
      sudo apt install -y python3 python3-pip
      ```

 - **Install latest version of Git**:
    6. Use the following command to install Git to your instance:
      ```bash
      sudo apt install -y git
      ```

- **Install Beautiful Soup**:
    7. Use the following command to install Beautiful Soup to your instance:
    ```bash
    pip3 install boto3 beautifulsoup4
    ```

- **Install Beautiful Soup**:
    8. Use the following command to install Beautiful Soup to your instance:
    ```bash
    pip3 install boto3 beautifulsoup4
    ```

- **Install install AWSCLI**:
    7. Use the following command to install install AWSCLI to your instance:
    ```bash
    pip install awscli
    ```

- **Clone the GitHub repository**:
    9. Use the following command to clone the GitHub repository to your instance:
    ```bash
    git clone https://github.com/your-username/your-repository.git
    ```

- **Navigate into the cloned repository**:
    10. Use the following command to Navigate into the cloned repository in your instance:
     ```bash
     cd your-repository-name
     ```

- **Run Code from the cloned repository**:
    11. Use the following command to run the python code on your instance:
     ```bash
     python3 GoogleTakeout.py
     ```

     You will start seeing all of your text and call data loading and sorting in your CLI to DynamoDB


    <h1>Project Reflections: Challenges and Learning with New Tools</h1>
    <p>Throughout this project, one of the main challenges I faced was implementing new coding techniques and working with tools that were outside of my usual stack. Adapting to new programming paradigms while parsing large datasets proved to be a learning curve, especially when dealing with the complexities of structured and unstructured data.
     Thankfully, tools like <strong>ChatGPT-4</strong> and <strong>Amazon Q Developer</strong> were invaluable. ChatGPT-4 helped clarify concepts I struggled with and provided quick solutions to coding errors or new techniques I needed to understand on the fly. Additionally, Amazon Q Developer proved to be an excellent resource for navigating AWS services and 
    optimizing my usage of DynamoDB for efficient storage and retrieval of parsed data.</p>

  - **Core Use of Data Parsing in Business**
    This project wasn’t just about overcoming technical challenges. The real power of parsing large volumes of data lies in what it can do for a business. As a company, being able to automatically organize and process client data allows us to.
        
     
    - **Repurpose old and new clients**: By structuring data efficiently, we can better understand client behavior and preferences, allowing us to re-engage them with targeted campaigns.
    - **Create text lists for promotions**: With properly parsed and organized data, generating contact lists for promotions becomes easier, helping us reach the right audience at the right time.
    - **Increase sales**: Leveraging the insights from parsed data allows us to offer more personalized services, improving client retention and ultimately driving sales.
    
    - **This project reinforced the importance of data-driven decision-making and how automating processes like this can have a tangible impact on business outcomes.**
