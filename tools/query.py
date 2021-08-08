import boto3
dynamodb = boto3.resource('dynamodb', region_name='eu-west-3')

table = dynamodb.Table('rainNext')
response = table.query(
  TableName="rainNext",
  KeyConditionExpression="#DYNOBASE_siteId = :pkey and #DYNOBASE_eventTime > :skey",
  ExpressionAttributeValues={
  ":pkey": 1,
  ":skey": 1628414100
},
  ExpressionAttributeNames={
  "#DYNOBASE_siteId": "siteId",
  "#DYNOBASE_eventTime": "eventTime",
  "#DYNOBASE_notified": "notified"
},
  Limit=100,
  FilterExpression="attribute_exists(#DYNOBASE_notified)",
)