import asyncio
import boto3
import discord
import flcc_dbhandler as fldb
import os
import time
import uuid
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from datetime import datetime, timezone
from discord.ext import commands
from flcc_loghandler import CloudwatchLogger

log_group = os.environ["LOGGROUP"]
fl_logger = CloudwatchLogger(log_group)

async def write_log(message:str):
    text = fl_logger.log(message)
    print(text)

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

def check_rank(acceptable_rank:list, perm_set="FL"):
    async def predicate(ctx):
        ranks = fldb.getUserInfo(f"{ctx.message.author.id}", "PermIDs")
        if perm_set in ranks and ranks[perm_set] in acceptable_rank:
            return True
        elif "GBL" in ranks and ranks["GBL"] in acceptable_rank:
            return True
        else:
            raise commands.MissingPermissions(acceptable_rank)
    return commands.check(predicate)

async def add_log(ctx, member, action:str, reason="No Reason Given"):

    infrac_id = str(uuid.uuid4())
    infrac_time = "{:%Y-%m-%d %H:%M:%S}".format(ctx.message.created_at)

    try:
        table = dynamodb.Table("Failed_Labs_Moderation_Log")
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
        await write_log(f"[DynamoDB Access]: {e.response['Error']['Message']}")
        return None, None, None
    else:
        return True, infrac_id, infrac_time

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        await write_log(f"[System]: Moderation Cog Loaded")

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
            embed.add_field(name="Reason", value=f"{reason}", inline=False)
            embed.add_field(name="Time", value=f"{infrac_time}", inline=False)
            embed.add_field(name="Infraction ID", value=f"`{infrac_id}`", inline=False)
            embed.set_author(name=f"{member}", icon_url=f"{member.avatar_url}")
            embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

            await ctx.send(embed=embed)
            await write_log(f"[Moderation]: {ctx.message.author} warned {member} for {reason}")

    @commands.command()
    @check_rank(["DEV", "ADMIN", "MOD"])
    async def kick(self, ctx, member: discord.Member, *, reason="No Reason Given"):
        success, infrac_id, infrac_time = await add_log(ctx, member, "Kick", reason)

        if success:
            embed = discord.Embed(
                color = discord.Color.orange(),
                title = ":boot:   Kicked   :boot:"
            )
            embed.add_field(name="Reason", value=f"{reason}", inline=False)
            embed.add_field(name="Time", value=f"{infrac_time}", inline=False)
            embed.add_field(name="Infraction ID", value=f"`{infrac_id}`", inline=False)
            embed.set_author(name=f"{member}", icon_url=f"{member.avatar_url}")
            embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

            #await member.kick(reason=reason)

            await ctx.send(embed=embed)
            await write_log(f"[Moderation]: {ctx.message.author} kicked {member} for {reason}")
        

    @commands.command()
    @check_rank(["DEV", "ADMIN"])
    async def ban(self, ctx, member: discord.Member, *, reason="No Reason Given"):

        # executer_info = fldb.getUserInfo(f"{ctx.message.author.id}")
        # member_info = fldb.getUserInfo(f"{member.id}")

        

        success, infrac_id, infrac_time = await add_log(ctx, member, "Ban", reason)

        if success:
            embed = discord.Embed(
                color = discord.Color.dark_red(),
                title = ":no_entry:   Banned   :no_entry:"
            )
            embed.add_field(name="Reason", value=f"{reason}", inline=False)
            embed.add_field(name="Time", value=f"{infrac_time}", inline=False)
            embed.add_field(name="Infraction ID", value=f"`{infrac_id}`", inline=False)
            embed.set_author(name=f"{member}", icon_url=f"{member.avatar_url}")
            embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

            #await member.ban(reason=reason)

            await ctx.send(embed=embed)
            await write_log(f"[Moderation]: {ctx.message.author} banned {member} for {reason}")

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
            await write_log(f"[Moderation]: Purging {amount} messages from {ctx.channel}")
            await asyncio.sleep(1)

            deleted_messages = await ctx.channel.purge(limit=amount+2)

            purge_log_filename = f"message-purge-{datetime.utcnow()}-{ctx.channel.name}".replace(" ", "T").replace(":", ".")

            embed = discord.Embed(
                color = discord.Color.green(),
                title = ":white_check_mark:   Message Purge   :white_check_mark:",
                description = f"Purged {amount} Messages."
            )
            embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

            await ctx.send(embed=embed, delete_after=10)

            await write_log(f"[Moderation]: {ctx.message.author} purged {amount} messages from {ctx.channel}")

            await write_log(f"[Moderation]: Writing {purge_log_filename} purge log.")

            with open(f"./tmp/{purge_log_filename}.txt", "w") as f:
                for message in deleted_messages:
                    f.write(f"[{message.created_at}]: [{message.author.name}#{message.author.discriminator} ({message.author.id})]: {message.clean_content}\n")

            await write_log(f"[S3 Access]: Sending {purge_log_filename} purge log to Amazon S3.")

            s3 = boto3.resource("s3", region_name="us-west-2")
            flcc_bucket = s3.Bucket("failedlabs-bot")

            try:
                with open(f"./tmp/{purge_log_filename}.txt", "rb") as data:
                    flcc_bucket.upload_fileobj(data, f"Purge Logs/{purge_log_filename}.txt")
            except Exception as e:
                await write_log(f"[S3 Access]: Upload Failed: {e}")
            else:
                await write_log(f"[S3 Access]: Upload Successful")

            await write_log(f"[Moderation]: Deleting {purge_log_filename} purge log.")

            os.remove(f"./tmp/{purge_log_filename}.txt")

def setup(bot):
    bot.add_cog(Moderation(bot))