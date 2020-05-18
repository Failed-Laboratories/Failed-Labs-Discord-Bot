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

async def add_log(ctx, member, action:str, reason="No Reason Given"):

    infrac_id = str(uuid.uuid4())
    infrac_time = "{:%Y-%m-%d %H:%M:%S}".format(ctx.message.created_at)

    try:
        table = dynamodb.Table("FLCC_Moderation_Log")
        table.put_item(
            Item={
                "InfractionID": infrac_id,
                "Date": infrac_time,
                "Action": action,
                "OffenderDUID": str(member.id),
                "ModeratorDUID": str(ctx.message.author.id),
                "Reason": str(reason)
            }
        )
    except ClientError as e:
        await write_log(e.response['Error']['Message'])
        return {"Success": False, "InfracID": None, "InfracTime": None}
    else:
        return {"Success": True, "InfracID": infrac_id, "InfracTime": infrac_time}


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        await write_log(f"[{datetime.utcnow()}]: [System]: Moderation Cog Loaded")

    #Commands
    @commands.command()
    @check_rank(["DEV", "ADMIN", "MOD"])
    async def warn(self, ctx, member:discord.Member, *, reason="No Reason Given"):
        success, infrac_id, infrac_time = await add_log(ctx, member, "Warn", reason)

        if success:
            embed = discord.Embed(
                color = discord.Color.orange(),
                title = ":exclamation:   Warned   :exclamation:"
            )
            embed.add_field(name="Reason", value=f"{reason}")
            embed.set_author(name=f"{member}", icon_url=f"{member.avatar_url}")
            embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

            await ctx.send(embed=embed)
            await write_log(f"[{ctx.message.created_at}]: [Moderation]: {ctx.message.author} warned {member} for {reason}")

    @commands.command()
    @check_rank(["DEV", "ADMIN", "MOD"])
    async def kick(self, ctx, member: discord.Member, *, reason="No Reason Given"):
        success, infrac_id, infrac_time = await add_log(ctx, member, "Kick", reason)

        if success:
            embed = discord.Embed(
                color = discord.Color.orange(),
                title = ":boot:   Kicked   :boot:"
            )
            embed.add_field(name="Reason", value=f"{reason}")
            embed.set_author(name=f"{member}", icon_url=f"{member.avatar_url}")
            embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

            #await member.kick(reason=reason)

            await ctx.send(embed=embed)
            await write_log(f"[{ctx.message.created_at}]: [Moderation]: {ctx.message.author} kicked {member} for {reason}")
        

    @commands.command()
    @check_rank(["DEV", "ADMIN"])
    async def ban(self, ctx, member: discord.Member, *, reason="No Reason Given"):
        success, infrac_id, infrac_time = await add_log(ctx, member, "Ban", reason)

        if success:
            embed = discord.Embed(
                color = discord.Color.dark_red(),
                title = ":no_entry:   Banned   :no_entry:"
            )
            embed.add_field(name="Reason", value=f"{reason}")
            embed.set_author(name=f"{member}", icon_url=f"{member.avatar_url}")
            embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

            #await member.ban(reason=reason)

            await ctx.send(embed=embed)
            await write_log(f"[{ctx.message.created_at}]: [Moderation]: {ctx.message.author} banned {member} for {reason}")

    @commands.command()
    @check_rank(["DEV", "ADMIN", "MOD"])
    async def purge(self, ctx, amount=5):
        async with ctx.typing():
            embed = discord.Embed(
                color = discord.Color.orange(),
                title = ":arrows_counterclockwise:   Message Purge   :arrows_counterclockwise:",
                description = f"Purging {amount} Messages..."
            )
            embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")
            
            await ctx.send(embed=embed)
            await write_log(f"[{ctx.message.created_at}]: [Moderation]: Purging {amount} messages from {ctx.channel}")
            await asyncio.sleep(1)
            await ctx.channel.purge(limit=amount+2)

            embed = discord.Embed(
                color = discord.Color.green(),
                title = ":white_check_mark:   Message Purge   :white_check_mark:",
                description = f"Purged {amount} Messages"
            )
            embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

            await ctx.send(embed=embed, delete_after=5)

            await write_log(f"[{ctx.message.created_at}]: [Moderation]: {ctx.message.author} purged {amount} messages from {ctx.channel}")

def setup(bot):
    bot.add_cog(Moderation(bot))