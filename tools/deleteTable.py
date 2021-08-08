#! /usr/bin/python3
# coding: utf-8

import boto3

tableName = "rainNext"
dyC = boto3.client('dynamodb')
dyC.delete_table(TableName=tableName)
waiter = dyC.get_waiter('table_not_exists')
waiter.wait(TableName=tableName)
