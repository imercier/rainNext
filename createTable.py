#! /usr/bin/python3
# coding: utf-8

import boto3
import botocore.session

tableName="toto"

dynamodb = boto3.resource('dynamodb')
table = dynamodb.create_table(
    TableName=tableName,
    KeySchema=[
        {
            'AttributeName': 'dataTime',
            'KeyType': 'HASH'  #Partition key
        },
        {
            'AttributeName': 'eventTime',
            'KeyType': 'RANGE'  #Sort key
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'dataTime',
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
