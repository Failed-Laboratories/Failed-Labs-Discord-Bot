import aiohttp
import asyncio
import boto3
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

async def write_log(message):
    print(message)
    with open(f"./logs/cmds-{datetime.date(datetime.utcnow())}.log", "a") as f:
        f.write(message + "\n")

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

def check_rank(acceptable_rank:list):
    async def predicate(ctx):
        table = dynamodb.Table("FLCC_User_Ranks")
        try:
            response = table.get_item(
                Key={
                    "DiscordUID": f"{ctx.message.author.id}"
                }
            )
        except ClientError as e:
            await write_log(f"[{datetime.utcnow()}]: [Database Access]: {e.response['Error']['Message']}")
            return False
        else:
            item = response["Item"]
            if item["PermID"] in acceptable_rank:
                return True
            else:
                raise commands.MissingPermissions(acceptable_rank)
    return commands.check(predicate)

def truncate(number, digits):
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper

class Statistics(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #events
    @commands.Cog.listener()
    async def on_ready(self):
        await write_log(f"[{datetime.utcnow()}]: [System]: Statistics Cog Loaded")

    
    #commands
    @commands.command()
    async def stats(self, ctx):
        mem_stats = dict(psutil.virtual_memory()._asdict())
        mem_tot = truncate(mem_stats["total"]/1000000, 2)
        mem_used = truncate(mem_stats["used"]/1000000, 2)
        cpu_per = psutil.cpu_percent()

        embed = discord.Embed(
            color = discord.Color.blurple(),
            title = ":bar_chart:   Resource Statistics   :bar_chart:",
        )
        # embed.add_field(name="Bot Creator", value="tycoonlover1359")
        embed.add_field(name="CPU Usage", value=f"{cpu_per}%")
        embed.add_field(name="Total Memory", value=f"{mem_tot} MB")
        embed.add_field(name="Used Memory", value=f"{mem_used} MB")
        # embed.add_field(name="Available Memory", value=f"{mem_ava} MB")
        # embed.add_field(name="Percent Used", value=str(mem_stats["percent"]))
        # embed.add_field(name="Percent Free", value=str(100-mem_stats["percent"]))
        embed.set_footer(text="Bot by Tycoonlover1359\nFailed Labs Central Command")

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Statistics(bot))