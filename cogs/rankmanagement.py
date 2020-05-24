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
        userdata = {}
        member = ctx.message.author
        userdata = fldb.getUserInfo(f"{member.id}")
        if userdata != {} or userdata != "Error":
            fl_ranks = {}
            json.load(open("./files/fl_ranks.json"))
            fl_perms = {}
            json.load(open("./files/fl_permissions.json"))
            sa_ranks = {}
            json.load(open("./files/sa_ranks.json"))
            sa_perms = {}
            json.load(open("./files/sa_permissions.json"))

            embed = discord.Embed(
                color = discord.Color.blue(),
                description = "hello"
            )
            embed.set_author(name=f"{member}", icon_url=f"{member.avatar_url}")
            
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(RankManagement(bot))
