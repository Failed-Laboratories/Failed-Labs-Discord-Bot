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

class ErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        await write_log(f"[{datetime.utcnow()}]: [System]: Error Handler Cog Loaded")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await write_log(f"[{ctx.message.created_at}]: [Error]: {error}")
        send_message = False
        set_footer = False
        embed = discord.Embed(
            color = discord.Color.dark_red(),
            title = ":warning: Error :warning:"
        )

        if isinstance(error, ClientError):
            embed.add_field(name="Error Message", value="An error has occurred while accessing the database. If this continues, please alert the developer immediately.")
            send_message = True
            set_footer = True

        if isinstance(error, commands.MissingPermissions):
            embed.add_field(name="Error Message", value="You do not have permission to use this command.")
            send_message = True
            set_footer = False

        if isinstance(error, commands.MissingRequiredArgument):
            embed.add_field(name="Error Message", value="Missing Required Arguments")
            send_message = True
            set_footer = False
        
        if isinstance(error, commands.ExtensionNotLoaded):
            embed.add_field(name="Error Message", value="Extension Not Loaded")
            send_message = True
            set_footer = True

        if send_message:
            if set_footer:
                embed.set_footer(text=f"Error: \n{error}")
            await ctx.send(embed=embed, delete_after=10)

    #Commands

def setup(bot):
    bot.add_cog(ErrorHandler(bot))