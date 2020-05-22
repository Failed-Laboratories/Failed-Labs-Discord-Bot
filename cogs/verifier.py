import aiohttp
import asyncio
import boto3
import discord
import flcc_dbhandler as fldb
import json
import logging
import random
import time
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from datetime import datetime, timezone
from discord.ext import commands

async def write_log(message):
    print(message)
    with open(f"./logs/cmds-{datetime.date(datetime.utcnow())}.log", "a") as f:
        f.write(message + "\n")

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

def check_rank(acceptable_rank:list, perm_set="FL"):
    async def predicate(ctx):
        ranks = fldb.getUserInfo(f"{ctx.message.author.id}", "PermIDs")
        if perm_set in ranks and ranks[perm_set] in acceptable_rank in acceptable_rank:
            return True
        elif "GBL" in ranks and ranks["GBL"] in acceptable_rank:
            return True
        else:
            raise commands.MissingPermissions(acceptable_rank)
    return commands.check(predicate)

def gen_verify_phrase():
    with open("./files/authdict.txt") as word_list:
        words = word_list.readlines()

    for x in range (0, len(words)):
        words[x] = words[x].replace("\n", "")

    first_word = random.sample(words,1)
    auth_phrase = first_word[0]

    for x in range (0, 5):

        joiners = [" and ", " the ", " do ", " can ", " is ", " a "]
        concater = random.sample(joiners, 1)
        word = random.sample(words, 1)

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
    async def verify(self, ctx):

        table = dynamodb.Table("FLCC_Users")
        author = ctx.message.author
        do_verify = True
        verified = False
        r_uid = ""
        r_uname = ""

        await write_log(f"[{datetime.utcnow()}]: [Verification]: Initiating verification for {ctx.message.author.name}")

        userData = fldb.getUserInfo(f"{author.id}", "RobloxUID")
        if userData != {}:
            await write_log(f"[{datetime.utcnow()}]: [Verification]: Verification for {ctx.message.author.name} failed: User already linked to a Roblox account.")
            do_verify = False

            embed = discord.Embed(
                color = discord.Color.dark_red(),
                title = ":warning:   Roblox Account Verification Error   :warning:",
                description = "You already have an account linked to your Discord profile!"
            )

            await ctx.send(embed=embed)

        if do_verify:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.blox.link/v1/user/{author.id}") as response:
                    if response.status == 200:
                        data = json.loads(await response.text())
                        if "error" not in data:
                            r_uid = data["primaryAccount"]
                            async with session.get(f"https://api.roblox.com/users/{r_uid}") as response:
                                if response.status == 200:
                                    data = json.loads(await response.text())
                                    r_uname = data["Username"]
                                    do_verify = False
                                    verified = True
                

        if do_verify:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://verify.eryn.io/api/user/{author.id}") as response:
                    if response.status == 200:
                        data = json.loads(await response.text())
                        if "error" not in data:
                            r_uid = data["robloxId"]
                            r_uname = data["robloxUsername"]
                            do_verify = False
                            verified = True

        if str(ctx.channel.type) != "private" and do_verify:

            embed = discord.Embed(
                color = discord.Color.blue(),
                title = ":globe_with_meridians:   Roblox Account Verification   :globe_with_meridians:",
                description = f"{ctx.message.author.mention} Check your DMs!"
            )

            await ctx.send(embed=embed, delete_after=5)

        if do_verify:

            embed = discord.Embed(
                color = discord.Color.orange(),
                title = ":globe_with_meridians:   Roblox Account Verification   :globe_with_meridians:",
                description = "Please tell me the username of the Roblox account you'd like to verify."
            )
            embed.set_footer(text="This prompt will expire in 15 seconds. \nFailed Labs Central Command")

            await author.send(embed=embed)

            def checkAuthor(m):
                return m.author == ctx.message.author

            try:
                msg = await self.bot.wait_for("message", check=checkAuthor, timeout=15)
            except asyncio.TimeoutError as e:
                await write_log(f"[{datetime.utcnow()}]: [Verification]: Verification for {ctx.message.author.name} failed: Username prompt timed out.")
                embed = discord.Embed(
                    color = discord.Color.dark_red(),
                    title = ":warning:   Roblox Account Verification Error   :warning:",
                    description = f"Prompt timed out. \nPlease try again or contact a staff member for more assistance."
                )
                embed.set_footer(text="Failed Labs Central Command")
                await author.send(embed=embed)
                do_verify = False
            else:
                r_uname = msg.content

                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://api.roblox.com/users/get-by-username?username={r_uname}") as response:
                        if response.status == 200:
                            data = json.loads(await response.text())
                            if "success" in data:

                                embed = discord.Embed(
                                    color = discord.Color.dark_red(),
                                    title = ":warning:   Roblox Account Verification Error   :warning:",
                                    description = f"Roblox User `{r_uname}` Not Found. Please Try Again."
                                )
                                embed.set_footer(text="Failed Labs Central Command")

                                await ctx.send(embed=embed)
                                await write_log(f"[{datetime.utcnow()}]: [Verification]: Verification for {ctx.message.author.name} failed: Unknown Roblox username.")
                                do_verify = False
                            else:
                                r_uid = data["Id"]

        if do_verify:

            auth_code = gen_verify_phrase()
            await write_log(f"[{datetime.utcnow()}]: [Verification]: Verification code for {ctx.message.author.name} to {r_uname}: {auth_code}.")

            verify_by_status = discord.File(
                fp = "./files/verifybystatus.png",
                filename = "verifybystatus.png",
                spoiler = False
            )
            verify_by_profile = discord.File(
                fp = "./files/verifybyprofile.png",
                filename = "verifybyprofile.png",
                spoiler = False
            )

            embed = discord.Embed(
                color = discord.Color.orange(),
                title = ":globe_with_meridians:   Roblox Account Verification   :globe_with_meridians:",
                description = f"Hello {author.mention}!\n\nYou will be verifying the following Roblox account: ```{r_uname}```\nGo to https://www.roblox.com/feeds/ and paste this code into your **status**, or you can go to https://www.roblox.com/my/account and paste this code into your **profile**:"
            )

            await author.send(embed=embed, files=[verify_by_status, verify_by_profile])

            embed = discord.Embed(
                color = discord.Color.orange(),
                description = f"```{auth_code}```"
            )

            await author.send(embed=embed)

            embed = discord.Embed(
                color = discord.Color.orange(),
                description = "Don't worry about telling me when you've finished. I'll check your status automatically and rank you if I find the code above.\n\nI will indicate to you that I am still checking your status by 'typing'. If I stop, the prompt has timed out and you will need to run the verify command again."
            )

            embed.set_footer(text="This prompt will expire in 60 seconds.\nFailed Labs Central Command")

            await author.send(embed=embed)
            

            do_verify = False
            check_status = True
            x = 0

            async with author.typing():
                while check_status and x <= 60:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"https://users.roblox.com/v1/users/{r_uid}/status") as response:
                            if response.status == 200:
                                data = json.loads(await response.text())
                                if data["status"] == auth_code:
                                    check_status = False
                                    verified = True
                                    break
                        await asyncio.sleep(0.5)
                        async with session.get(f"https://users.roblox.com/v1/users/{r_uid}") as response:
                            if response.status == 200:
                                data = json.loads(await response.text())
                                description = data["description"]
                                if description.find(auth_code) != -1:
                                    check_status = False
                                    verified = True
                                    break
                                x = x + 1
                                await asyncio.sleep(0.5)

        if verified:

            await write_log(f"[{datetime.utcnow()}]: [Verification]: Verification for {ctx.message.author.name} to {r_uname} successful.")

            embed = discord.Embed(
                color = discord.Color.green(),
                title = ":white_check_mark:   Roblox Account Verification   :white_check_mark:",
                description = f"Verification of Roblox User `{r_uname}` to {author.mention} Successful!"
            )
            embed.set_footer(text="Failed Labs Central Command")

            await author.edit(
                nick=f"{r_uname}",
                reason=f"User successfully verified and linked to Roblox account with id {r_uid} and username {r_uname}"
            )

            try:
                response = table.get_item(
                    Key={
                        "DiscordUID": f"{author.id}"
                    }
                )
            except ClientError as e:
                await write_log(e.response['Error']['Message'])
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
                                ":ruid": str(r_uid)
                            }
                        )
                    except ClientError as e:
                        await write_log(e.response['Error']['Message'])
                    else:
                        pass
                else:
                    fldb.createNewUser(
                        DiscordUID = f"{author.id}",
                        DiscordUName = f"{author.name}",
                        DiscordUDiscriminator = f"{author.discriminator}",
                        RobloxUID = f"{r_uid}",
                        RobloxUName = f"{r_uname}"
                    )

        elif verified == False and do_verify == False:

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