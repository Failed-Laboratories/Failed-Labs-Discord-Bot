import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb", region_name="us-west-2")

def lambda_handler(event, context):
    records = event["Records"]
    for record in records:
        
        offenderDUID = record["dynamodb"]["NewImage"]["OffenderDUID"]["S"]
        action = record["dynamodb"]["NewImage"]["Action"]

        print(offenderDUID)
        print(action)
        
        log_table = dynamodb.Table("FLCC_Moderation_Log")
        mods_table = dynamodb.Table("FLCC_User_Moderations")
        
        try:
            response = mods_table.get_item(
                    Key={
                        "DiscordUID": str(offenderDUID)
                    }
                )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            pass
        
        if "Item" not in response:
            if action == "Ban":
                response = mods_table.put_item(
                    Item={
                        "DiscordUID": str(offenderDUID),
                        "Banned": True,
                        "Kicks": "0",
                        "Warns": "0"
                    }    
                )
            elif action == "Kick":
                response = mods_table.put_item(
                    Item={
                       "DiscordUID": str(offenderDUID),
                       "Banned": False,
                       "Kicks": "1",
                       "Warns": "0"
                    }
                )
            elif action == "Warn":
                response = mods_table.put_item(
                    Item={
                        "DiscordUID": str(offenderDUID),
                        "Banned": False,
                        "Kicks": "0",
                        "Warns": "1"
                    }
                )
        else:
            curr_kicks = int(response["Item"]["Kicks"])
            curr_warns = int(response["Item"]["Warns"])
            print(curr_kicks)
            print(curr_warns)
            if action == "Ban":
                try:
                    response = mods_table.update_item(
                        Key={
                            "DiscordUID": str(offenderDUID)
                        },
                        UpdateExpression="set Banned=:b",
                        ExpressionAttributeValues={
                            ":b": True
                        }
                    )
                except ClientError as e:
                    print(e.response['Error']['Message'])
                else:
                    pass
            elif action == "Kick":
                try:
                    response = mods_table.update_item(
                        Key={
                            "DiscordUID": str(offenderDUID)
                        },
                        UpdateExpression="set Kicks=:k",
                        ExpressionAttributeValues={
                            ":k": str(curr_kicks + 1)
                        }
                    )
                except ClientError as e:
                    print(e.response['Error']['Message'])
                else:
                    pass
            elif action == "Warn":
                try:
                    response = mods_table.update_item(
                        Key={
                            "DiscordUID": str(offenderDUID)
                        },
                        UpdateExpression="set Warns=:w",
                        ExpressionAttributeValues={
                            ":w": str(curr_warns + 1)
                        }
                    )
                except ClientError as e:
                    print(e.response['Error']['Message'])
                else:
                    pass
    return "Success!"

event = {"Records":[{"eventID":"de4b712975b8c462838d0ac363bfd5de","eventVersion":"1.1","dynamodb":{"Keys":{"InfractionNum":{"S":"123456"}},"NewImage":{"OffenderDUID":{"S":"123456"},"Action":{"S":"Ban"},"Reason":{"S":"Test Reason"},"ModeratorDUID":{"S":"1234"}},"StreamViewType":"NEW_AND_OLD_IMAGES","SequenceNumber":"1036300000000012122594657","SizeBytes":"129","ApproximateCreationDateTime":"1588906531.0"},"awsRegion":"us-west-2","eventName":"INSERT","eventSourceARN":"arn:aws:dynamodb:us-west-2:651915650471:table/FLCC_Users/stream/2020-05-08T00:23:25.710","eventSource":"aws:dynamodb"}]}

lambda_handler(event, None)