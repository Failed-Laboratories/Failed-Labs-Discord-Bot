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
                await write_log(e.response['Error']['Message'])
                return False
        else:
            item = response["Item"]
            if item["PermID"] in acceptable_rank:
                return True
            else:
                raise commands.MissingPermissions(acceptable_rank)
    return commands.check(predicate)
    
class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        await write_log(f"[{datetime.utcnow()}]: [System]: Help Cog Loaded")

    #Commands
    @commands.group(name="help", invoke_without_command=True)
    async def help(self, ctx):
        embed = discord.Embed(
            color = discord.Color.greyple(),
            title = ":grey_question:   Help   :grey_question:"
        )
        embed.set_footer(text="Failed Labs Central Command")
        embed.add_field(name="\> Developer [4] <", value="`load`, `unload`, `reload`, `shutdown`")
        embed.add_field(name="\> Moderation [3] <", value="`kick`, `ban`, `purge`", inline=False)
        embed.add_field(name="\> Miscellaneous [1] <", value="`ping`", inline=False)
        embed.add_field(name="\> Statistics [1] <", value="`stats`", inline=False)
        embed.add_field(name="\> Verification [1] <", value="`verify`", inline=False)

        await ctx.send(embed=embed)
    
    #Developer commands
    @help.command()
    async def load(self, ctx):
        embed = discord.Embed(
            color = discord.Color.greyple(),
            title = ":grey_question:   Help   :grey_question:",
            description = "Developer Commands - `load`"
        )
        embed.set_footer(text="Failed Labs Central Command")
        embed.add_field(name="Description", value="Loads a command module (cog).")
        embed.add_field(name="Usage", value="`load <module filename>`", inline=False)
        embed.add_field(name="Required Level", value="Developer")

        await ctx.send(embed=embed)
    
    @help.command()
    async def unload(self, ctx):
        embed = discord.Embed(
            color = discord.Color.greyple(),
            title = ":grey_question:   Help   :grey_question:",
            description = "Developer Commands - `unload`"
        )
        embed.set_footer(text="Failed Labs Central Command")
        embed.add_field(name="Description", value="Unloads a command module (cog).")
        embed.add_field(name="Usage", value="`unload <module filename>`", inline=False)
        embed.add_field(name="Required Level", value="Developer")

        await ctx.send(embed=embed)

    @help.command()
    async def reload(self, ctx):
        embed = discord.Embed(
            color = discord.Color.greyple(),
            title = ":grey_question:   Help   :grey_question:",
            description = "Developer Commands - `reload`"
        )
        embed.set_footer(text="Failed Labs Central Command")
        embed.add_field(name="Description", value="Reloads a command module (cog).")
        embed.add_field(name="Usage", value="`reload <module filename>`", inline=False)
        embed.add_field(name="Required Level", value="Developer")

        await ctx.send(embed=embed)

    @help.command()
    async def shutdown(self, ctx):
        embed = discord.Embed(
            color = discord.Color.greyple(),
            title = ":grey_question:   Help   :grey_question:",
            description = "Developer Commands - `shutdown`"
        )
        embed.set_footer(text="Failed Labs Central Command")
        embed.add_field(name="Description", value="Shutsdown the bot, terminating the process gracefully.")
        embed.add_field(name="Usage", value="`shutdown`", inline=False)
        embed.add_field(name="Required Level", value="Developer")

        await ctx.send(embed=embed)

    #Moderation Commands
    @help.command()
    async def kick(self, ctx):
        embed = discord.Embed(
            color = discord.Color.greyple(),
            title = ":grey_question:   Help   :grey_question:",
            description = "Moderation Commands - `kick`"
        )
        embed.set_footer(text="Failed Labs Central Command")
        embed.add_field(name="Description", value="Kicks a user from the server.")
        embed.add_field(name="Usage", value="`kick <user (mention or ID)> [reason]`", inline=False)
        embed.add_field(name="Required Level", value="Moderator")

        await ctx.send(embed=embed)

    @help.command()
    async def ban(self, ctx):
        embed = discord.Embed(
            color = discord.Color.greyple(),
            title = ":grey_question:   Help   :grey_question:",
            description = "Moderation Commands - `ban`"
        )
        embed.set_footer(text="Failed Labs Central Command")
        embed.add_field(name="Description", value="Bans a user from the server.")
        embed.add_field(name="Usage", value="`ban <user (mention or ID)> [reason]`", inline=False)
        embed.add_field(name="Required Level", value="Administrator")

        await ctx.send(embed=embed)

    @help.command()
    async def purge(self, ctx):
        embed = discord.Embed(
            color = discord.Color.greyple(),
            title = ":grey_question:   Help   :grey_question:",
            description = "Moderation Commands - `purge`"
        )
        embed.set_footer(text="Failed Labs Central Command")
        embed.add_field(name="Description", value="Mass deletes messages from the current channel.")
        embed.add_field(name="Usage", value="`purge [amount (default is 5)]`", inline=False)
        embed.add_field(name="Required Level", value="Moderator")

        await ctx.send(embed=embed)

    #Miscellaneous Commands
    @help.command()
    async def ping(self, ctx):
        embed = discord.Embed(
            color = discord.Color.greyple(),
            title = ":grey_question:   Help   :grey_question:",
            description = "Miscellaneous Commands - `ping`"
        )
        embed.set_footer(text="Failed Labs Central Command")
        embed.add_field(name="Description", value="Returns a ping pong ball. And the bot's latency.")
        embed.add_field(name="Usage", value="`ping`", inline=False)
        embed.add_field(name="Required Level", value="Visitor")

        await ctx.send(embed=embed)
    
    #Statistics Commands
    @help.command()
    async def stats(self, ctx):
        embed = discord.Embed(
            color = discord.Color.greyple(),
            title = ":grey_question:   Help   :grey_question:",
            description = "Statistics Commands - `stats`"
        )
        embed.set_footer(text="Failed Labs Central Command")
        embed.add_field(name="Description", value="Displays the bot's current resource usage statistics.")
        embed.add_field(name="Usage", value="`stats`", inline=False)
        embed.add_field(name="Required Level", value="Visitor")

        await ctx.send(embed=embed)

    #Verification Commands
    @help.command()
    async def verify(self, ctx):
        embed = discord.Embed(
            color = discord.Color.greyple(),
            title = ":grey_question:   Help   :grey_question:",
            description = "Verification Commands - `verify`"
        )
        embed.set_footer(text="Failed Labs Central Command")
        embed.add_field(name="Description", value="Verifies ownership of a Roblox account, linking it to the current Discord user.")
        embed.add_field(name="Usage", value="`verify <Roblox username>`", inline=False)
        embed.add_field(name="Required Level", value="Visitor")

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Help(bot))