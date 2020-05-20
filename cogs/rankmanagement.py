import aiohttp
import asyncio
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

def check_rank(acceptable_rank:list):
    async def predicate(ctx):
        rank = fldb.getUserInfo(f"{ctx.message.author.id}", "PermID")
        if rank in acceptable_rank:
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
        userdata = {}
        member = ctx.message.author
        userdata = fldb.getUserInfo(f"{member.id}")
        if userdata != {} or userdata != "Error":
            async with aiohttp.ClientSession() as session:
                pass
            ranks = json.load(open("./files/ranks.json"))
            userRank = ranks[userdata["RankID"]]["Name"]
            perms = json.load(open("./files/permissions.json"))
            userPerm = perms[userdata["PermID"]]
            embed = discord.Embed(
                color = discord.Color.blue()
                description = ""
            )
            embed.set_author(name=f"{member}", icon_url=f"{member.avatar_url}")
            
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(RankManagement(bot))
