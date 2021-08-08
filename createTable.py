#! /usr/bin/python3
# coding: utf-8

import boto3
import botocore.session

dynamodb = boto3.resource('dynamodb')

tableName = "rainNext"
table = dynamodb.create_table(
    TableName=tableName,
    KeySchema=[
        {
            'AttributeName': 'siteId',
            'KeyType': 'HASH'  # Partition key
        },
        {
            'AttributeName': 'eventTime',
            'KeyType': 'RANGE'  # Sort key
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'siteId',
            'AttributeType': 'N'
        },
        {
            'AttributeName': 'eventTime',
            'AttributeType': 'N'
        },

    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

print("Table status:", table.table_status)
session = botocore.session.get_session()
dynamodb = session.create_client('dynamodb')
waiter = dynamodb.get_waiter('table_exists')
waiter.wait(TableName=tableName)
