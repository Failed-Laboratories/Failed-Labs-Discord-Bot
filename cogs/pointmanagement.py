import aiohttp
import asyncio
import boto3
import csv
import flcc_dbhandler as fldb
import discord
import json
import logging
import math
import os
import random
import time
import uuid
from botocore.exceptions import ClientError
from datetime import datetime, timezone
from discord.ext import commands
from flcc_loghandler import CloudwatchLogger

log_group = os.environ["LOGGROUP"]
fl_logger = CloudwatchLogger(log_group)

async def write_log(message:str):
    text = fl_logger.log(message)
    print(text)

def check_rank(acceptable_rank:list, perm_set="FL"):
    async def predicate(ctx):
        ranks = fldb.getUserInfo(f"{ctx.message.author.id}", "PermIDs")
        if perm_set in ranks and ranks[perm_set] in acceptable_rank:
            return True
        elif "GBL" in ranks and ranks["GBL"] in acceptable_rank:
            return True
        else:
            raise commands.MissingPermissions(acceptable_rank)
    return commands.check(predicate)

class PointsManagement(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        await write_log(f"[System]: Points Management Cog Loaded")

    #Commands
    @commands.group(name="points", invoke_without_command=True)
    @check_rank(["DEV", "EXEC"])
    async def points(self, ctx, user:discord.User, new_rank:str):
        embed = discord.Embed(
            color = discord.Color.blue(),
            title = "User Rank Updater",
            timestamp = datetime.utcnow()
        )
        embed.add_field(name="User to Update", value=user.mention)
        embed.add_field(name="New Rank", value=new_rank)

        await ctx.send(embed=embed)

    @points.command(name="set")
    @check_rank(["DEV", "EXEC"])
    async def setrank(self, ctx, user:discord.User, new_points:int):
        embed = discord.Embed(
            color = discord.Color.blue(),
            title = "User Points Updater",
            description = "Please confirm that the following information is correct: ",
            timestamp = datetime.utcnow()
        )
        embed.set_footer(text=f"This prompt will expire in 15 seconds \n{ctx.message.author} | Failed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

        user_info = fldb.getUserInfo(user.id)

        embed.add_field(name="User to Update", value=f"**Discord:** {user.mention}\n**Roblox:** [{user_info['RobloxUName']}](https://roblox.com/users/profile?username={user_info['RobloxUName']})")
        embed.add_field(name="Old Points", value=f"{user_info['Points']}", inline=False)
        embed.add_field(name="New Points", value=f"{new_points}", inline=False)

        message = await ctx.send(embed=embed)

        await message.add_reaction(emoji="✅")
        await message.add_reaction(emoji="❌")

        def checkReactions(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in ["✅", "❌"]

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=15, check=checkReactions)
        except asyncio.TimeoutError as e:
            pass
        else:
            await message.clear_reactions()
                                
            if str(reaction.emoji) == "✅":
                embed = discord.Embed(
                    color = discord.Color.orange(),
                    title = "User Points Updater",
                    description = "Confirmed. Updating...",
                    timestamp = datetime.utcnow()
                )
                embed.set_footer(text="Failed Labs Central Command")

                await message.edit(embed=embed)
            else:
                embed = discord.Embed(
                    color = discord.Color.dark_red(),
                    title = "User Points Updater",
                    description = "Point change cancelled. No changes have been made.",
                    timestamp = datetime.utcnow()
                )


    @points.group(name="bulksetpoints", aliases=["bulk"], invoke_without_command=True)
    @check_rank(["DEV", "EXEC"])
    async def bulksetpoints(self, ctx):

        bulk_point_update_example_csv = discord.File(
            fp = "./files/bulkpointupdateexample.csv",
            filename="bulk_point_update_example.csv",
            spoiler=False
        )

        embed = discord.Embed(
            color = discord.Color.orange(),
            title = "🛡️   Bulk Points Updater   🛡️",
            description = "Please use this example file to create a Comma-Seperated Values file with the Roblox usernames of people who have earned (or lost) points, followed by the ammount of points lost or gained.\n\nWhen you are finished and ready to submit this CSV file, ensure that it has a file extension of `.csv` (for example, the file name can be `bulk_point_update.csv`), then run the command `:points set bulk submit` to submit a bulk point update.",
            timestamp = datetime.utcnow()
        )
        embed.set_footer(text=f"Failed Labs Central Command")

        await ctx.send(embed=embed)
        await ctx.send(file=bulk_point_update_example_csv)
    
    @bulksetpoints.command(name="submit", aliasses=["submit"])
    @check_rank(["DEV", "EXEC"])
    async def bulkpointssubmit(self, ctx):
        await write_log(f"[Rank Management]: Discord User ID '{ctx.message.author.id}' initiated bulk points update. Awaiting file...")
        embed = discord.Embed(
            color = discord.Color.orange(),
            title = "🛡️   Bulk Points Updater   🛡️",
            description = "To ensure that I properly parse and extract the data you give me, please ensure that it meets the following criteria:\n\n**1.)** The file extension of your file is `.csv`.\n\n**2.)** the *first* line of your file looks like this:\n```csv\nrobloxusername,points```\nIf your file does not meet all the criteria I described above, please edit it so that it does. Then, restart this command so I can parse your file.",
            timestamp = datetime.utcnow()
        )
        embed.set_footer(text=f"This prompt will expire in 15 seconds \n{ctx.message.author} | Failed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

        message = await ctx.send(embed=embed)

        def checkMessage(m):
            return m.attachments != [] and m.author == ctx.message.author
        
        try:
            author_message = await self.bot.wait_for("message", check=checkMessage, timeout=15)
        except asyncio.TimeoutError as e:
            await write_log(f"[Rank Management]: Prompt timed out - file from '{ctx.message.author.id}' never received.")

            embed = discord.Embed(
                color = discord.Color.dark_red(),
                title = "⚠️   Bulk Points Updater Error   ⚠️",
                description = "Prompt timed out. Please try again.",
                timestamp = datetime.utcnow()
            )
            embed.set_footer(text="Failed Labs Central Command")

            await message.edit(embed=embed)
        else:
            await write_log(f"[Rank Management]: File from '{ctx.message.author.id}' received successfully. Parsing...")

            embed = discord.Embed(
                color = discord.Color.green(),
                title = "🔄   Bulk Points Updater   🔄",
                description = "File Received. Parsing File...",
                timestamp = datetime.utcnow()
            )
            embed.set_footer(text=f"{ctx.message.author} | Failed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

            await message.edit(embed=embed)

            await asyncio.sleep(1)

            author_attachments = author_message.attachments

            for file in author_attachments:
                filename = file.filename
                file_url = file.url
                temp_file_name = f"bulk-user-update-{random.randint(111,999)}.csv"
                if not filename.endswith(".csv"):
                    embed = discord.Embed(
                        color = discord.Color.dark_red(),
                        title = "⚠️   Bulk Points Updater Error   ⚠️",
                        description = "File type is not `.csv`. Please run the `:points set bulk submit` command again and ensure your file extension is `.csv`.",
                        timestamp = datetime.utcnow()
                    )
                    embed.set_footer(text=f"{ctx.message.author} | Failed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

                    await message.edit(embed=embed)
                else:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(file_url) as response:
                            if response.status == 200:
                                file_data = await response.text()
                                with open("./tmp/" + temp_file_name, "w+") as f:
                                    f.write(file_data.replace("\n", ""))

                    await author_message.delete()

                    try:
                        csv_file = open("./tmp/" + temp_file_name, newline="")
                    except FileNotFoundError as e:
                        embed = discord.Embed(
                            color = discord.Color.dark_red(),
                            title = "⚠️   Bulk Points Updater Error   ⚠️",
                            description = "An error occurred while parsing the file you submitted. Please try again or contact the developer if this problem persists.",
                            timestamp = datetime.utcnow()
                        )
                        embed.set_footer(text=f"Error: {e}\nFailed Labs Central Command")

                        await message.edit(embed=embed)
                    else:
                        embed = discord.Embed(
                            color = discord.Color.green(),
                            title = "🛡️   Bulk Points Updater   🛡️",
                            description = "Data parsing completed.\n\nIf I've done this correctly, you should see a list of usernames followed by numbers, as shown below. These correspond to the Roblox username of the user and the amount of points they've earned. Below the example data, you should see the first three data points you gave me. Please check to make sure I've parsed and extraced the data correctly.",
                            timestamp = datetime.utcnow()
                        )
                        embed.set_footer(text=f"This prompt will expire in 15 seconds.\n{ctx.message.author} | Failed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

                        csv_data = dict()
                        sample_data = dict()
                        reader = csv.reader(csv_file)
                        header = next(reader)
                        i = 0

                        for row in reader:
                            if row != []:
                                roblox_username = str(row[0])
                                points_to_add = str(row[1])
                                if points_to_add.startswith("-"):
                                    points_to_add = "-" + points_to_add.lstrip("-").lstrip("0")
                                else:
                                    points_to_add = int(points_to_add)

                                csv_data[roblox_username] = points_to_add

                                if i < 3: 
                                    sample_data[roblox_username] = points_to_add

                        example_data = {
                            "returnofthewarlock": "2727",
                            "tycoonlover1359": "1359",
                            "creeperraptor04": "-404"
                        }
                        
                        embed.add_field(name="Example Data", value=f"```json\n{json.dumps(example_data, indent=4)}```", inline=False)
                        embed.add_field(name="Your Data", value=f"```json\n{json.dumps(sample_data, indent=4)}```", inline=False)

                        await message.edit(embed=embed)
                        await message.add_reaction(emoji="✅")
                        await message.add_reaction(emoji="❌")

                        def checkReactions(reaction, user):
                            return user == author_message.author and str(reaction.emoji) in ["✅", "❌"]

                        try:
                            reaction, user = await self.bot.wait_for("reaction_add", timeout=15, check=checkReactions)
                        except asyncio.TimeoutError as e:
                            pass
                        else:
                            await message.clear_reactions()
                                
                            if str(reaction.emoji) == "✅":

                                request_time = datetime.utcnow()

                                embed = discord.Embed(
                                    color = discord.Color.orange(),
                                    title = "🔄   Bulk Points Updater   🔄",
                                    description = "Uploading data to Amazon S3. Please wait...",
                                    timestamp = datetime.utcnow()
                                )
                                embed.set_footer(text=f"{ctx.message.author} | Failed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

                                csv_data["Request Info"] = {
                                    "RequesterDUID": f"{ctx.message.author.id}",
                                    "Time": f"{request_time}",
                                    "UUID": f"{uuid.uuid4()}"
                                }

                                await message.edit(embed=embed)

                                s3 = boto3.resource("s3", region_name="us-west-2")
                                flcc_bucket = s3.Bucket("failedlabs-bot")

                                bulk_json_data = f"bulk-point-request-{request_time}-{ctx.message.author.id}".replace(" ", "T").replace(":", ".")

                                with open(f"./tmp/{bulk_json_data}.json", "w") as f:
                                    f.write(json.dumps(csv_data, indent=4))

                                try:
                                    with open(f"./tmp/{bulk_json_data}.json", "rb") as data:
                                        response = flcc_bucket.upload_fileobj(data, f"Bulk Requests/{bulk_json_data}.json")
                                except Exception as e:
                                    embed = discord.Embed(
                                        color = discord.Color.dark_red(),
                                        title = "⚠️   Bulk Points Updater Error   ⚠️",
                                        description = "An error occurred while uploading data to Amazon S3. Please try again. If this issue persists, contact the developer immediately.",
                                        timestamp = datetime.utcnow()
                                    )
                                    embed.set_footer(text=f"Error: {e}\nFailed Labs Central Command")
                                
                                    await message.edit(embed=embed)
                                else:
                                    embed = discord.Embed(
                                        color = discord.Color.orange(),
                                        title = "🔄   Bulk Points Updater   🔄",
                                        description = "Upload to Amazon S3 successful. Handing off to AWS Lambda...",
                                        timestamp = datetime.utcnow()
                                    )
                                    embed.set_footer(text=f"{ctx.message.author} | Failed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

                                    await message.edit(embed=embed)

                                    lambda_payload = {
                                        "filename": f"{bulk_json_data}.json"
                                    }

                                    awslambda = boto3.client("lambda", region_name="us-west-2")

                                    awslambda.invoke(
                                        InvocationType="Event",
                                        FunctionName="arn:aws:lambda:us-west-2:160477935000:function:FL-BOT_BulkPointsChange",
                                        Payload=str.encode(str(lambda_payload).replace("'", '"'))
                                    )

                                    await asyncio.sleep(1)

                                    embed = discord.Embed(
                                        color = discord.Color.green(),
                                        title = "✅   Bulk Points Updater   ✅",
                                        description = "Handoff to AWS Lambda successful.\n\nYour bulk points request is now processing. Note that it may take up to 5 minutes before processing is completed and propegated to the Failed Labs User Database, and then an additional 5 minutes before my cache is updated to reflect the new user information.",
                                        timestamp = datetime.utcnow()
                                    )
                                    embed.set_footer(text=f"{ctx.message.author} | Failed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

                                    os.remove(f"./tmp/{bulk_json_data}.json")

                                    await message.edit(embed=embed)

                            else:
                                embed = discord.Embed(
                                    color = discord.Color.dark_red(),
                                    title = "❌   Bulk Points Updater   ❌",
                                    description = "Rank change cancelled. Your changes have not been submitted and no database changes will occur.",
                                    timestampe = datetime.utcnow()
                                )
                                embed.set_footer(text=f"{ctx.message.author} | Failed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")
                                
                                await message.edit(embed=embed)

def setup(bot):
    bot.add_cog(PointsManagement(bot))