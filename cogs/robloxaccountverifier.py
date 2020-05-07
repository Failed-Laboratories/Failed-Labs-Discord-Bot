import asyncio
import boto3
import decimal
import discord
import io
import json
import random
import time
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from datetime import datetime, timezone
from discord.ext import commands
from urllib import request

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

async def write_log(message):
    print(message)
    with open(f"./logs/cmds-{datetime.date(datetime.utcnow())}.log", "a") as f:
        f.write(message + "\n")

def gen_verify_phrase():
    with open("authdict.txt") as word_list:
        words = word_list.readlines()

    for x in range (0, len(words)):
        words[x] = words[x].replace("\n", "")

    first_word = random.sample(words,1)
    auth_phrase = first_word[0]

    for x in range (0, 5):

        joiners = [" and ", " the ", " do ", " can ", " is ", " a "]
        concater = random.sample(joiners, 1)
        word = random.sample(words,1)

        new_phrase = concater[0] + word[0]
        auth_phrase += new_phrase
    
    return auth_phrase


class RobloxAccountVerifier(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        await write_log(f"[{datetime.utcnow()}]: [System]: Roblox Account Verifier Cog Loaded")

    #Commands
    @commands.command()
    async def verify(self, ctx, r_uname:str):

        await write_log(f"[{datetime.utcnow()}]: [Verification]: Initiating verification for {ctx.message.author.name} to {r_uname}")

        table = dynamodb.Table("Failed_Labs_Central_Command_Database")
        author = ctx.message.author
        do_verify = True

        try:
            response = table.get_item(
                Key={
                    "DiscordUID": f"{author.id}"
                }
            )
        except ClientError as e:
            write_log(e.response['Error']['Message'])
        else:
            if "Item" in response:
                if "RobloxUID" in response["Item"]:
                    await write_log(f"[{datetime.utcnow()}]: [Verification]: Verification for {ctx.message.author.name} to {r_uname} failed: User already linked to a Roblox account.")
                    do_verify = False

                    embed = discord.Embed(
                        color = discord.Color.dark_red(),
                        title = ":warning:   Roblox Account Verification Error   :warning:",
                        description = "You already have an account linked to your Discord profile!"
                    )

                    await ctx.send(embed=embed)

        if do_verify:

            r_uid = ""

            resp = request.urlopen(f"https://api.roblox.com/users/get-by-username?username={r_uname}")
            data = json.loads(resp.read().decode("UTF-8"))

            if "success" in data:

                embed = discord.Embed(
                    color = discord.Color.dark_red(),
                    title = ":warning:   Roblox Account Verification Error   :warning:",
                    description = f"Roblox User `{r_uname}` Not Found. Please Try Again."
                )
                embed.set_footer(text="Failed Labs Central Command")

                await ctx.send(embed=embed)
                await write_log(f"[{datetime.utcnow()}]: [Verification]: Verification for {ctx.message.author.name} to {r_uname} failed: Unknown Roblox username.")
                do_verify = False
            
            try:
                response = table.scan(
                    ProjectionExpression="DiscordUID, RobloxUID",
                    FilterExpression=Key("RobloxUID").eq(str(data["Id"]))
                )
            except ClientError as e:
                write_log(e.response['Error']['Message'])
            else:
                items = response["Items"]

            for x in items:
                if "DiscordUID" in items[x]:
                    embed = discord.Embed(
                        color = discord.Color.dark_red(),
                        title = ":warning:   Roblox Account Verification Error   :warning:",
                        description = f"Roblox User `{r_uname}` is already linked to an account.\nPlease try again or contact a staff member for more assistance."
                    )
                    embed.set_footer(text="Failed Labs Central Command")

                    await ctx.send(embed=embed)
                    await write_log(f"[{datetime.utcnow()}]: [Verification]: Verification for {ctx.message.author.name} to {r_uname} failed: Roblox user already linked to a Discord account.")
                    do_verify = False

        if str(ctx.channel.type) != "private" and do_verify:

            embed = discord.Embed(
                color = discord.Color.blue(),
                title = ":globe_with_meridians:   Roblox Account Verification   :globe_with_meridians:",
                description = f"{ctx.message.author.mention} Check your DMs!"
            )

            await ctx.send(embed=embed)

        auth_code = gen_verify_phrase()
        await write_log(f"[{datetime.utcnow()}]: [Verification]: Verification code for {ctx.message.author.name} to {r_uname}: {auth_code}.")

        if do_verify:
            r_uid = data["Id"]
            embed = discord.Embed(
                color = discord.Color.orange(),
                title = ":globe_with_meridians:   Roblox Account Verification   :globe_with_meridians:",
                description = f"Hello {author.mention}!\n\nYou will be verifying the following Roblox account: ```{r_uname}```\nGo to https://www.roblox.com/feeds/ and paste this code into your **status**: ```{auth_code}```\nDon't worry about telling me when you've finished. I'll check your status automatically and rank you if I find the code above.\n\nI will indicate to you that I am still checking your status by 'typing'. If you see me stop, the prompt has timed out and you will need to run the verify command again."
            )
            embed.set_footer(text="This prompt will expire in 60 seconds.\nFailed Labs Central Command")

            resp = request.urlopen("https://cdn.glitch.com/34d846a5-187e-4fda-a891-a65b043e5995%2Fverifyhelp.png?v=1588729383987")
            verify_help_picture = discord.File(
                fp = io.BytesIO(resp.read()),
                filename = "verify_help_pic.png",
                spoiler = False
            )

            await author.send(embed=embed, file=verify_help_picture)

            verified = False
            check_status = True
            x = 0

            async with author.typing():
                while check_status and x <= 60:
                    resp = request.urlopen(f"https://users.roblox.com/v1/users/{r_uid}/status")
                    data = json.loads(resp.read().decode("UTF-8"))
                    if data["status"] == auth_code:
                        check_status = False
                        verified = True
                        break
                    x = x + 1
                    await asyncio.sleep(1)

                if verified:

                    await write_log(f"[{datetime.utcnow()}]: [Verification]: Verification for {ctx.message.author.name} to {r_uname} successful.")
                
                    embed = discord.Embed(
                        color = discord.Color.green(),
                        title = ":white_check_mark:   Roblox Account Verification   :white_check_mark:",
                        description = f"Verification of Roblox User `{r_uname}` to {author.mention} Successful!"
                    )
                    embed.set_footer(text="Failed Labs Central Command")

                    try:
                        response = table.get_item(
                            Key={
                                "DiscordUID": f"{author.id}"
                            }
                        )
                    except ClientError as e:
                        write_log(e.response['Error']['Message'])
                    else:
                        if "Item" in response:
                            try:
                                response = table.update_item(
                                    Key={
                                        "DiscordUID": f"{author.id}"
                                    },
                                    UpdateExpression="set RobloxUID=:ruid, RobloxUName=:run",
                                    ExpressionAttributeValues={
                                        ":run": r_uname,
                                        ":ruid": r_uid
                                    }
                                )
                            except ClientError as e:
                                write_log(e.response['Error']['Message'])
                            else:
                                pass
                        else:
                            try:
                                response = table.put_item(
                                    Item={
                                        "DiscordUID": f"{author.id}",
                                        "DiscordUName": f"{author.name}",
                                        "DiscordUDiscriminator": f"{author.discriminator}"  ,
                                        "RobloxUID": r_uid,
                                        "RobloxUName": r_uname,
                                        "Warnings": 0,
                                        "Banned": False,
                                        "Kicks": 0,
                                        "RankID": "BLEH"
                                    }
                                )
                            except ClientError as e:
                                write_log(e.response['Error']['Message'])
                            else:
                                pass

                elif verified == False:

                    await write_log(f"[{datetime.utcnow()}]: [Verification]: Verification for {ctx.message.author.name} to {r_uname} failed: Verification timed out.")

                    embed = discord.Embed(
                        color = discord.Color.dark_red(),
                        title = ":x:   Roblox Account Verification   :x:",
                        description = f"Verification of Roblox User `{r_uname}` to {author.mention} Failed.\nI couldn't find the code I gave you in your status.\n\nPlease try again or contact a staff member for more assistance."
                    )
                    embed.set_footer(text="Failed Labs Central Command")
                
                await author.send(embed=embed)
                    




def setup(bot):
    bot.add_cog(RobloxAccountVerifier(bot))