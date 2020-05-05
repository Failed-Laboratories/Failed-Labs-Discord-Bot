from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

def to_decimal(num:float):
    return decimal.Decimal(num)

def create_item(table:str, item:dict):
    #Create and item within an Amazon DynamoDB table. Returns the info about the request as a dict object.
    table = dynamodb.Table(table)
    response = table.put_item(
        Item = item
    )
    return response

def update_item(table:str, key:dict, update_expression:str, update_values:dict, return_values="UPDATED_NEW"):
    #Update an item within a DynamoDB table. By default, this only returns the update values as a dict object.
    table = dynamodb.Table(table)
    response = table.update_item(
        Key = key,
        UpdateExpression = update_expression,
        ExpressionAttributeValues = update_values,
        ReturnValues = return_values
    )
    return response

def read_item(table:str, key:dict):
    #Read an item within a DynamoDB table. Returns the item as a json object.
    table = dynamodb.Table(table)
    response = table.get_item(
        Key=key
    )
    item = response["Item"]
    return item

def delete_item(table:str, key:dict):
    #Deletes an item within a DynamoDB table. Returns the info about the request as a dict object
    table = dynamodb.Table(table)
    response = table.delete_item(
        Key=key
    )
    return response
