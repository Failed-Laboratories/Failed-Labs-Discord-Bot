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

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

async def write_log(message):
    print(message)
    with open(f"./logs/cmds-{datetime.date(datetime.utcnow())}.log", "a") as f:
        f.write(message + "\n")

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


class RankManagement(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        await write_log(f"[{datetime.utcnow()}]: [System]: Rank Management Cog Loaded")

    #Commands
    @commands.group(name="rank", invoke_without_command=True)
    async def rank(self, ctx, member:discord.Member):
        embed = discord.Embed(
            color = discord.Color.orange()
        )

        try:
            table = dynamodb.Table("FLCC_User")
            userdata = {}
            response = table.get_item(
                Key = {
                    "DiscordUID": f"{member.id}"
                }
            )
        except boto3.client("dynamodb").exceptions.ResourceNotFoundException as e:
            await write_log(f"[{datetime.utcnow()}]: [Database Access]: {e.response['Error']['Message']}")
            embed = discord.Embed(
                color = discord.Color.dark_red(),
                title = ":warning: Error :warning:"
            )
            embed.add_field(name="Error Message", value="An error occurred while accessing the database. Please contact the developer if this continues.")
        except ClientError as e:
            await write_log(f"[{datetime.utcnow()}]: [Database Access]: {e.response['Error']['Message']}")
            embed = discord.Embed(
                color = discord.Color.dark_red(),
                title = ":warning: Error :warning:"
            )
            embed.add_field(name="Error Message", value="An error occurred while accessing the database. Please contact the developer if this continues.")
        else:
            pass
        
        embed.set_author(name=f"{member}", icon_url=f"{member.avatar_url}")
        
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(RankManagement(bot))
