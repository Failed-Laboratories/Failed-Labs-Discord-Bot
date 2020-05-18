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
        table = dynamodb.Table("FLCC_Users")
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

class Miscellaneous(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #events
    @commands.Cog.listener()
    async def on_ready(self):
        await write_log(f"[{datetime.utcnow()}]: [System]: Miscellaneous Cog Loaded")

    #Commands
    @commands.command()
    async def ping(self, ctx):

        embed = discord.Embed(
            color = discord.Color.green(),
            title = ":ping_pong:   Pong!   :ping_pong:",
            description = f"Latency: {round(self.bot.latency * 1000)} ms"
        )

        embed.set_footer(text="Failed Labs Central Command")

        await ctx.send(embed=embed)

    @commands.command()
    async def test(self, ctx, iter:int):
        embed = discord.Embed(
            color = discord.Color.green(),
            title = "Testing",
            description = iter*":ping_pong:"
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def pfp(self, ctx):
        profilePic = str(ctx.message.author.avatar_url_as(static_format="jpg", size=4096))
        await ctx.send(profilePic)

def setup(bot):
    bot.add_cog(Miscellaneous(bot))