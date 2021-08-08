#! /usr/bin/python3
# coding: utf-8

import boto3
from botocore.exceptions import ClientError

SENDER = "Meteo Alert <ivan.mercier+alert@gmail.com>"
RECIPIENT = "ivan.mercier+alert@gmail.com"
SUBJECT = "Rain's coming!"
BODY_TEXT = ("Amazon SES Test (Python)\r\n"
             "This email was sent with Amazon SES using the "
             "AWS SDK for Python (Boto).")
CHARSET = "UTF-8"
client = boto3.client('ses')
try:
    response = client.send_email(
        Destination={
            'ToAddresses': [
                RECIPIENT,
            ],
        },
        Message={
            'Body': {
                'Text': {
                    'Charset': CHARSET,
                    'Data': BODY_TEXT,
                },
            },
            'Subject': {
                'Charset': CHARSET,
                'Data': SUBJECT,
            },
        },
        Source=SENDER,
    )
except ClientError as e:
    print(e.response['Error']['Message'])
else:
    print("Email sent! Message ID:"),
    print(response['MessageId'])
