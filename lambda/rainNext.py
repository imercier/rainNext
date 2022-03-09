#! /usr/bin/python3
# coding: utf-8

from meteofrance_api import MeteoFranceClient
import time
import boto3
import os


def getForecast():
    client = MeteoFranceClient()
    resp = client.get_rain(latitude=43.2959994, longitude=5.3754487)
    return resp


def dbSav(table, getTime, forecast, siteId):
    with dyT.batch_writer() as batch:
        for f in forecast.forecast:
            f["siteId"] = siteId
            f["forecastTime"] = forecast.updated_on
            f["getTime"] = getTime
            f["eventTime"] = f.pop("dt")
            batch.put_item(Item=f)


def sendMail(forecast, siteId):
    mailSender = os.environ['MAILSENDER']
    mailDest = os.environ['MAILDEST']
    SUBJECT = "Rain's coming! Site {0}".format(siteId)
    BODY_TEXT = printForecast(forecast)
    CHARSET = "UTF-8"
    client = boto3.client('ses')
    client.send_email(
        Destination={'ToAddresses': [mailDest, ], },
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
        Source=mailSender,
    )


def alert(table, getTime, forecast, siteId):
    # rain intented?
    rains = next((d for d in forecast.forecast if d.get("rain") != 1), None)
    if rains:
        # already notified from 2 hours ago?
        response = table.query(
            TableName="rainNext",
            KeyConditionExpression="#siteId = :pkey and #eventTime > :skey",
            ExpressionAttributeValues={
                ":pkey": siteId,
                ":skey": getTime - 7200
            },
            ExpressionAttributeNames={
                "#siteId": "siteId",
                "#eventTime": "eventTime",
                "#notified": "notified"
            },
            FilterExpression="attribute_exists(#notified)",
        )
        if response["Count"] == 0:
            sendMail(forecast, siteId)
            for f in forecast.forecast:
                table.update_item(
                    Key={
                        'siteId': siteId,
                        'eventTime': f["eventTime"]
                    },
                    UpdateExpression="set notified=:n",
                    ExpressionAttributeValues={
                        ':n': True
                    },
                    ReturnValues="UPDATED_NEW"
                )


def printForecast(forecast):
    forecastTime = time.strftime('%Hh%M',
                                 time.localtime(forecast.updated_on))
    s = 'Forecast at {0}:\n'.format(forecastTime)
    for f in forecast.forecast:
        t = time.strftime('%Hh%M', time.localtime(f["eventTime"]))
        s += '\t{0} à {1}\n'.format(f["desc"], t)
    return s


siteId = 1
getTime = int(time.time())
forecast = getForecast()
dyC = boto3.resource('dynamodb')
dyT = dyC.Table('rainNext')
dbSav(dyT, getTime, forecast, siteId)
alert(dyT, getTime, forecast, siteId)
