import json
import boto3

def lambda_handler(event, context):
    
    records = event["Records"]
    dynamodb = boto3.resource("dynamodb", region_name="us-west-2")
    users = dynamodb.Table("FLCC_Users")
    
    for i in records:
        if i["eventName"].lower() == "insert":
            record_data = i["dynamodb"]["NewImage"]
            offender = record_data["OffenderDUID"]["S"]
            action = record_data["Action"]["S"]
            response = users.get_item(
                    Key={
                        "DiscordUID": f"{offender}"
                    }
                )
            if "Item" in response:
                offender_data = response["Item"]
                current_warns = int(offender_data["Warns"])
                current_kicks = int(offender_data["Kicks"])
                update_expression = ""
                update_data = {}
                if action.lower() == "warn":
                    update_expression = "set Warns=:w"
                    update_data = {
                        ":w": f"{current_warns + 1}"
                    }
                elif action.lower() == "kick":
                    update_expression = "set Kicks=:k"
                    update_data = {
                        ":k": f"{current_kicks + 1}"
                    }
                elif action.lower() == "ban":
                    update_expression = "set Banned=:b"
                    update_data = {
                        ":b": True
                    }
                response = users.update_item(
                        Key={
                            "DiscordUID": f"{offender}"
                        },
                        UpdateExpression = update_expression,
                        ExpressionAttributeValues = update_data
                    )
                    
                return {
                    "statusCode": 200,
                    "body": "success"
                }
                
            else:
                return {
                    "statusCode": 200,
                    "body": "error occurred"
                }