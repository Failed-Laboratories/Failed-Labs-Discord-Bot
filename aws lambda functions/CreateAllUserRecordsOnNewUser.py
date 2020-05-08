import json
import boto3

dynamodb = boto3.resource("dynamodb", region_name="us-west-2")

def lambda_handler(event):
    ranks_table = dynamodb.Table("FLCC_User_Ranks")
    mods_table = dynamodb.Table("FLCC_User_Moderations")
    
    response = ranks_table.get_item(
            Key={
                "DiscordUID": str(event["DiscordUID"])
            }
        )
    
    print(response)

    if "Item" in response:
        pass
    else:
        #pass
        response = ranks_table.put_item(
                Item={
                    "DiscordUID": str(event["DiscordUID"]),
                    "Awards": {},
                    "PermID": "L1",
                    "Points": "0",
                    "RankID": "TRNE"
                }
            )
        
    response = mods_table.get_item(
            Key={
                "DiscordUID": str(event["DiscordUID"])
            }
        )

    print(response)
    
    if "Item" in response:
        pass
    else:
        #pass
        response = mods_table.put_item(
                Item={
                    "DiscordUID": str(event["DiscordUID"]),
                    "Warns": "0",
                    "Banned": False,
                    "Kicks": "0"
                }
            )
            
    return "Success!"

lambda_handler(
    event={
        "DiscordUID": "168556731134115840",
        "DiscordUName": "tycoonlover1359"
    }
)