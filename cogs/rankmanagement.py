import aiohttp
import asyncio
import boto3
import flcc_dbhandler as fldb
import decimal
import discord
import io
import json
import logging
import math
import os
import psutil
import random
import time
import uuid
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from datetime import datetime, timezone
from discord.ext import commands

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

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
            )
            embed.set_author(name=f"{member}", icon_url=f"{member.avatar_url}")
            embed.add_field(name="Rank", value=f"{userRank}", inline=False)
            embed.add_field(name="Permission Level", value=f"{userPerm}", inline=False)
            
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(RankManagement(bot))
