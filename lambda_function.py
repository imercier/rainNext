import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import os
from boto3.session import Session
import json


def jTree(jsonObject, id):
    return [obj for obj in jsonObject if obj['Id'] == id][0]['Name']


def sendMail(payload, mailObject):
    mailclient = boto3.client('ses', region_name=os.environ.get('AWS_REGION'))
    try:
        mailclient.send_email(
            Destination={
                'ToAddresses': os.environ.get('RECIPIENT').split(";")
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': "UTF-8",
                        'Data': payload,
                    },
                },
                'Subject': {
                    'Charset': "UTF-8",
                    'Data': mailObject,
                },
            },
            Source=os.environ.get('SENDER'),
        )
    except ClientError as e:
        print(e.response['Error']['Message'])


def lambda_handler(event, context):
    payload = ''
    now = datetime.utcnow()
    start = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    end = now.strftime('%Y-%m-%d')
    payload += ("Cost of %s (utc)" % (start) + "\n")
    accountTree = json.loads(os.environ.get('ACCOUNT'))

    sts_connection = boto3.client('sts')
    stsConnection = sts_connection.assume_role(
        RoleArn=os.environ.get('STSROLEARN'),
        RoleSessionName="fooRoleSessionName",
        ExternalId=os.environ.get('STSEXTERNALID')
    )
    cred = stsConnection['Credentials']
    session = Session(aws_access_key_id=cred['AccessKeyId'],
                      aws_secret_access_key=cred['SecretAccessKey'],
                      aws_session_token=cred['SessionToken'])

    costExlorerClient = session.client('ce')
    costType = 'BlendedCost'
    response = costExlorerClient.get_cost_and_usage(
            TimePeriod={'Start': start, 'End':  end},
            Granularity='DAILY', Metrics=[costType],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'LINKED_ACCOUNT'},
                {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                ],
            Filter={"Not": {"Dimensions": {"Key": "RECORD_TYPE", "Values": ["Credit", ]}}}
            )

    total = 0
    for result_by_time in response['ResultsByTime']:
        for group in result_by_time['Groups']:
            amount = float(group['Metrics']['BlendedCost']['Amount'])
            total += amount
            roundAmount = round(amount, 2)
            if roundAmount == 0:
                continue
            account = group['Keys'][0]
            accountName = jTree(accountTree['Accounts'], account)
            service = group['Keys'][1]
            payload += (account + "\t" + str(roundAmount) + "$\t" +
                        service + "\t\t [" + accountName + "]\n")

    payload += ("\nTotal blended cost (credits not deducted): " +
                str(round(total, 2)) + "$")
    mailObject = "[CloudLab] aws daily billing report " + start
    sendMail(payload, mailObject)

    if now.day == 1:
        payload = ''
        start = (now.replace(day=1) - timedelta(days=1)).replace(day=1).\
            strftime('%Y-%m-%d')
        end = now.strftime('%Y-%m-%d')
        response = costExlorerClient.get_cost_and_usage(
                TimePeriod={'Start': start, 'End':  end},
                Granularity='MONTHLY', Metrics=[costType],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'LINKED_ACCOUNT'},
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                    ],
                Filter={"Not": {"Dimensions": {"Key": "RECORD_TYPE", "Values": ["Credit", ]}}}
                )
        total = 0
        for result_by_time in response['ResultsByTime']:
            for group in result_by_time['Groups']:
                amount = float(group['Metrics']['BlendedCost']['Amount'])
                total += amount
                roundAmount = round(amount, 2)
                if roundAmount == 0:
                    continue
                account = group['Keys'][0]
                accountName = jTree(accountTree['Accounts'], account)
                service = group['Keys'][1]
                payload += (account + "\t" + str(roundAmount) + "$\t" +
                            service + "\t\t [" + accountName + "]\n")

        payload += ("\nTotal blended cost (credits not deducted): " +
                    str(round(total, 2)) + "$")
        mailObject = "[CloudLab] aws monthly billing report " + start
        sendMail(payload, mailObject)
