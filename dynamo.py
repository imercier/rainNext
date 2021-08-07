#! /usr/bin/python3
# coding: utf-8

from meteofrance_api import MeteoFranceClient
import time
import boto3


def test_rain():
    client = MeteoFranceClient()
    resp = client.get_rain(latitude=43.2959994, longitude=5.3754487)
    # {"dt": 1628360400, "rain": 1, "desc": "Temps sec"}
    return resp.forecast


def dbSav(table, time, forecast):
    with dyT.batch_writer() as batch:
        for f in forecast:
            f["dataTime"] = dataTime
            f.pop("desc")
            f["eventTime"] = f.pop("dt")
            batch.put_item(Item=f)


dataTime = int(time.time())
forecast = test_rain()
dyC = boto3.resource('dynamodb')
dyT = dyC.Table('rainNext')
dbSav(dyT, dataTime, forecast)

# will rain?
response = dyT.query(
        TableName="rainNext",
        KeyConditionExpression="#DYNOBASE_dataTime = :pkey",
        ExpressionAttributeValues={
            ":pkey": dataTime,
            ":rain": 1
            },
        ExpressionAttributeNames={
            "#DYNOBASE_dataTime": "dataTime",
            "#DYNOBASE_rain": "rain"
            },
        FilterExpression="#DYNOBASE_rain <> :rain",
        )
print(response['Items'])
