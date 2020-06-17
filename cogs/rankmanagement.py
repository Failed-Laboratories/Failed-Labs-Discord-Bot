import aiohttp
import asyncio
import csv
import flcc_dbhandler as fldb
import discord
import json
import logging
import math
import random
import time
from datetime import datetime, timezone
from discord.ext import commands

async def write_log(message):
    print(message)
    with open(f"./logs/cmds-{datetime.date(datetime.utcnow())}.log", "a") as f:
        f.write(message + "\n")

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

class RankManagement(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        await write_log(f"[{datetime.utcnow()}]: [System]: Rank Management Cog Loaded")

    #Commands
    @commands.group(name="rank", invoke_without_command=True)
    async def rank(self, ctx):
        author = ctx.message.author
        await write_log(f"[{datetime.utcnow()}]: [Rank Management]: Loading Rank Info for DiscordUID '{author.id}'")
        user_data = fldb.getUserInfo(f"{author.id}")
        if user_data != "Error" and user_data != {}:
            ranks_and_perms = json.load(open("./files/ranksandperms.json", "r"))

            await write_log(f"[{datetime.utcnow()}]: [Rank Management]: Getting Roblox Avatar Headshort for DiscordUID '{author.id}'")
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_data['RobloxUID']}&size=720x720&format=Png&isCircular=false") as response:
                    if response.status == 200:
                        data = json.loads(await response.text())
                        global avatar_thumbnail_url
                        avatar_thumbnail_url = data["data"][0]["imageUrl"] 


            ranks = ranks_and_perms["Ranks"]
            perms = ranks_and_perms["Permissions"]

            fl_ranks, fl_perms, sd_ranks, sd_perms = ranks["FL"], perms["FL"], ranks["SD"], perms["SD"]

            current_ranks = user_data["RankIDs"]
            current_perms = user_data["PermIDs"]
            current_fl_rank = "Not Ranked"
            current_sd_rank = "Not Ranked"
            current_fl_perm = "Not Applicable"
            current_sd_perm = "Not Applicable"

            if "FL" in current_ranks:
                current_fl_rank = fl_ranks[current_ranks["FL"]]["Name"]

            if "SD" in current_ranks:
                current_sd_rank = sd_ranks[current_ranks["SD"]]["Name"]

            if "GBL" in current_perms:
                current_fl_perm = fl_perms[current_perms["GBL"]]
                current_sd_perm = sd_perms[current_perms["GBL"]]
            else:
                if "FL" in current_perms:
                    current_fl_perm = fl_perms[current_perms["FL"]]
                if "SD" in current_perms:
                    current_sd_perm = fl_perms[current_perms["SD"]]

            desc = f"**Failed Labs Main Group** \n \
                     **Rank:** {current_fl_rank}\n \
                     **Permission Level:** {current_fl_perm} \n\n \
                     **Failed Labs Security Division** \n \
                     **Rank:** {current_sd_rank} \n \
                     **Permission Level:** {current_sd_perm}"

            if current_sd_rank != "Not Ranked":
                desc = desc + "\n\n**Security Division Rank Progress:**\n\n" + ""

            embed = discord.Embed(
                color = discord.Color.blue(),
                title = f'{user_data["RobloxUName"]} - Rank',
                description = desc,
                timestamp = datetime.utcnow()
            )
            embed.set_author(name=f"{author}", icon_url=f"{author.avatar_url}")
            embed.set_footer(text="Failed Labs Central Command")
            embed.set_thumbnail(url=f"{avatar_thumbnail_url}")

            #"**Rank Progress:**\n" + ":white_medium_square:"*int(user_data["Points"]) + 

            
            
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                color = discord.Color.dark_red(),
                description = "User Not Found",
                timestamp = datetime.utcnow()
            )
            embed.set_author(name=f"{author}", icon_url=f"{author.avatar_url}")
            embed.set_footer(text="Failed Labs Central Command")

            await ctx.send(embed=embed)
    
    @commands.group(name="setrank", invoke_without_command=True)
    @check_rank(["DEV"])
    async def setrank(self, ctx, user:discord.User, new_rank:str):
        embed = discord.Embed(
            color = discord.Color.blue(),
            title = "User Rank Updater",
            timestamp = datetime.utcnow()
        )
        embed.add_field(name="User to Update", value=user.mention)
        embed.add_field(name="New Rank", value=new_rank)

        await ctx.send(embed=embed)

    @setrank.group(name="bulksetrank", aliases=["bulk"], invoke_without_command=True)
    @check_rank(["DEV"])
    async def bulksetrank(self, ctx):

        bulk_rank_update_example_csv = discord.File(
            fp = "./files/bulkrankupdateexample.csv",
            filename="bulk_rank_update_example.csv",
            spoiler=False
        )

        embed = discord.Embed(
            color = discord.Color.orange(),
            title = "Bulk Rank Updater",
            description = "Please use this example file to create a Comma-Seperated Values file with the Roblox usernames of people who have earned (or lost) points, followed by the ammount of points lost or gained.\n\nWhen you are finished and ready to submit this CSV file, ensure that it has a file extension of `.csv` (for example, the file name can be `bulk_rank_update.csv`), then run the command `:setrank bulk submit` to submit a bulk rank update.",
            timestamp = datetime.utcnow()
        )
        embed.set_footer(text=f"Failed Labs Central Command")

        await ctx.send(embed=embed)
        await ctx.send(file=bulk_rank_update_example_csv)
    
    @bulksetrank.command(name="submit", aliasses=["submit"])
    @check_rank(["DEV"])
    async def bulkranksubmit(self, ctx):
        await write_log(f"[{datetime.utcnow()}]: [Rank Management]: Discord User ID '{ctx.message.author.id}' initiated bulk rank update. Awaiting file...")
        embed = discord.Embed(
            color = discord.Color.orange(),
            title = "Bulk Rank Updater",
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
            await write_log(f"[{datetime.utcnow()}]: [Rank Management]: Prompt timed out - file from '{ctx.message.author.id}' never received.")

            embed = discord.Embed(
                color = discord.Color.dark_red(),
                title = "⚠️   Bulk Rank Updater Error   ⚠️",
                description = "Prompt timed out. Please try again.",
                timestamp = datetime.utcnow()
            )
            embed.set_footer(text="Failed Labs Central Command")

            await message.edit(embed=embed)
        else:
            await write_log(f"[{datetime.utcnow()}]: [Rank Management]: File from '{ctx.message.author.id}' received successfully. Parsing...")

            embed = discord.Embed(
                color = discord.Color.green(),
                title = "Bulk Rank Updater",
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
                        title = "⚠️   Bulk Rank Updater Error   ⚠️",
                        description = "File type is not `.csv`. Please run the `:setrank bulk submit` command again and ensure your file extension is `.csv`.",
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
                            title = "⚠️   Bulk Rank Updater Error   ⚠️",
                            description = "An error occurred while parsing the file you submitted. Please try again or contact the developer if this problem persists.",
                            timestamp = datetime.utcnow()
                        )
                        embed.set_footer(text=f"Error: {e}\nFailed Labs Central Command")

                        await message.edit(embed=embed)
                    else:
                        embed = discord.Embed(
                            color = discord.Color.green(),
                            title = "Bulk Rank Updater",
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
                                embed = discord.Embed(
                                    color = discord.Color.green(),
                                    title = "Bulk Rank Updater",
                                    description = "Sending file to backend and queing AWS Lambda...",
                                    timestamp = datetime.utcnow()
                                )
                                embed.set_footer(text=f"{ctx.message.author} | Failed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

                                await message.edit(embed=embed)
                            else:
                                embed = discord.Embed(
                                    color = discord.Color.dark_red(),
                                    title = "Bulk Rank Updater",
                                    description = "Rank change cancelled. Your changes have not been submitted and no database changes will occur.",
                                    timestampe = datetime.utcnow()
                                )
                                embed.set_footer(text=f"{ctx.message.author} | Failed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")
                                
                                await message.edit(embed=embed)

def setup(bot):
    bot.add_cog(RankManagement(bot))
