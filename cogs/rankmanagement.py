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
        author = ctx.message.author
        userdata = fldb.getUserInfo(f"{author.id}")
        if userdata != {} or userdata != "Error":
            ranks_and_perms = json.load(open("./files/ranksandperms.json", "r"))

            embed = discord.Embed(
                color = discord.Color.blue(),
                description = "hello"
            )
            embed.set_author(name=f"{author}", icon_url=f"{author.avatar_url}")
            
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                color = discord.Color.dark_red()
            )
            embed.set_author(name=f"{author}", icon_url=f"{author.avatar_url}")

            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(RankManagement(bot))
