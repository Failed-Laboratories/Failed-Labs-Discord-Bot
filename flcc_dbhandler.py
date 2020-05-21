import boto3
from datetime import datetime
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb", region_name="us-west-2")

def write_log(message):
    print(message)
    with open(f"./logs/cmds-{datetime.date(datetime.utcnow())}.log", "a") as f:
        f.write(message + "\n")

def getUserInfo(userid:str, choice=None):
    write_log(f"[{datetime.utcnow()}]: [Database Access]: Getting Info For DiscordUID '{userid}'")
    try:
        table = dynamodb.Table("FLCC_Users")
        response = table.get_item(
            Key={
                "DiscordUID": f"{userid}"
            }
        )
    except ClientError as e:
        write_log(f"[{datetime.utcnow()}]: [Database Access]: {e.response['Error']['Message']}")
        return "Error"
    else:
        if "Item" in response:
            item = response["Item"]
            if choice != None and choice in item:
                return item[str(choice)]
            elif choice != None:
                return {}
            else:
                return item
        else:
            return {}

def createNewUser(DiscordUID:str, DiscordUName:str, DiscordUDiscriminator:str, RobloxUID:str, RobloxUName:str):
    try:
        table = dynamodb.Table("FLCC_Users")
        table.put_item(
            Item={
                "Awards": {},
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
        write_log(f"[{datetime.utcnow()}]: [Database Access]: {e.response['Error']['Message']}")
        return "Error"
    else:
        return "Success"
