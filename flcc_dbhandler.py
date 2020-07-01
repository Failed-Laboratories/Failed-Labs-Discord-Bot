import boto3
import json
import os
import time
from datetime import datetime
from botocore.exceptions import ClientError
from flcc_loghandler import CloudwatchLogger

dynamodb = boto3.resource("dynamodb", region_name="us-west-2")

users_table = "Failed_Labs_Users"

dbCache = {}

log_group = os.environ["LOGGROUP"]
fl_logger = CloudwatchLogger(log_group)

def write_log(message:str):
    text = fl_logger.log(message)
    print(text)

def check_cache(key:str):
    if key in dbCache and float(dbCache[key]["Timeout"]) > time.time():
        write_log(f"[DynamoDB Cache]: Accessing '{key}' from Cache")
        return dbCache[key]
    else:
        return {}

def write_cache(key:str, item:dict):
    write_log(f"[DynamoDB Cache]: Caching '{key}' for 327 seconds.")
    timeout = time.time() + 327
    dbCache[key] = item
    dbCache[key]["Timeout"] = str(timeout)

def getUserInfo(userid:str, choice=None):
    userInfo = check_cache(userid)

    if userInfo == {}:
        write_log(f"[DynamoDB Access]: Getting Info For DiscordUID '{userid}'")
        try:
            table = dynamodb.Table(users_table)
            response = table.get_item(
                Key={
                    "DiscordUID": f"{userid}"
                }
            )
        except ClientError as e:
            write_log(f"[DynamoDB Access]: {e.response['Error']['Message']}")
            return "Error"
        else:
            if "Item" in response:
                userInfo = response["Item"]
                write_cache(userid, userInfo)
            else:
                userInfo = {}

    if choice != None and choice in userInfo:
        userInfo = userInfo[str(choice)]
    elif choice != None:
        userInfo = {}
    return userInfo

def createNewUser(DiscordUID:str, DiscordUName:str, DiscordUDiscriminator:str, RobloxUID:str, RobloxUName:str):
    try:
        table = dynamodb.Table(users_table)
        table.put_item(
            Item={
                "Awards": [],
                "Banned": False,
                "DiscordUDiscriminator": DiscordUDiscriminator,
                "DiscordUID": DiscordUID,
                "DiscordUName": DiscordUName,
                "Kicks": "0",
                "PermIDs": {
                    "FL": "L1"
                },
                "Points": "0",
                "RankIDs": {
                    "FL": "SCI"
                },
                "RobloxUID": RobloxUID,
                "RobloxUName": RobloxUName,
                "Warns": "0"
            }
        )
    except ClientError as e:
        write_log(f"[DynamoDB Access]: {e.response['Error']['Message']}")
        return "Error"
    else:
        return "Success"
