import json
import boto3

dynamodb = boto3.resource("dynamodb", region_name="us-west-2")

def lambda_handler(event, context):
    
    return event

    # output = {}
    
    # query = event["queryStringParameters"]
    # discordUID = str(query["DiscordUID"])
    # choice = str(query["Choice"])
    
    # table = dynamodb.Table("FLCC_Users")
    
    # response = table.get_item(
    #     Key={
    #         "DiscordUID": str(discordUID)
    #     }    
    # )
    
    # if "Item" in response:
        
    #     output["status"] = "ok"
    #     item = response["Item"]
        
    #     if choice.lower() == "all":
    #         output["userInfo"] = item
    #     else:
    #         output["userInfo"] = item[choice]
        
    # else:
        
    #     output["status"] = "error"
    #     output["error"] = "User not found"
    
    # return output