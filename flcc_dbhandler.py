import boto3
from datetime import datetime
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb", region_name="us-west-2")
db = boto3.client("dynamodb")

def write_log(message):
    print(message)
    with open(f"./logs/cmds-{datetime.date(datetime.utcnow())}.log", "a") as f:
        f.write(message + "\n")

def getUserInfo(userid:str, choice=None):
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
        item = response["Item"]
        if choice != None and choice in item:
            return item[str(choice)]
        elif choice not in item:
            return "Error"
        else:
            return item

def createNewUser(DiscordUID:str, DiscordUName:str, DiscordUDiscriminator:str, RobloxUID:str, RobloxUName:str):
    try:
        table = dynamodb.Table("FLCC_Users")
        response = table.put_item(
            Item={
                "DiscordUID": DiscordUID,
                "DiscordUName": DiscordUName,
                "DiscordUDiscriminator": DiscordUDiscriminator,
                "RobloxUID": RobloxUID,
                "RobloxUName": RobloxUName
            }
        )
    except ClientError as e:
        write_log(f"[{datetime.utcnow()}]: [Database Access]: {e.response['Error']['Message']}")
        return "Error"
    else:
        return "Success"
