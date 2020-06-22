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
import uuid
from datetime import datetime, timezone
from discord.ext import commands

async def write_log(message):
    print(message)
    with open(f"./logs/cmds-{datetime.date(datetime.utcnow())}.log", "a") as f:
        f.write(message + "\n")

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

def setup(bot):
    bot.add_cog(RankManagement(bot))