import asyncio
import boto3
import discord
import flcc_dbhandler as fldb
import json
import math
import os
import pytz
from botocore.exceptions import ClientError
from datetime import datetime
from discord.ext import commands
from flcc_loghandler import CloudwatchLogger

log_group = os.environ["LOGGROUP"]
fl_logger = CloudwatchLogger(log_group)

async def write_log(message:str):
    text = fl_logger.log(message)
    print(text)

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

class LogManagement(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        await write_log(f"[System]: Log Management Cog Loaded")

    #Tasks

    #Commands
    @commands.command()
    @check_rank(["DEV"])
    async def upload_logs(self, ctx):
        author = ctx.message.author
        await write_log(f"[Log Management]: Promting {ctx.author} for confirmation.")
        embed = discord.Embed(
            color=discord.Color.orange(),
            title="📃   Log Management   📃",
            description="The action you are about to make may cause the bot to 'hang' for some time, possibly disconnecting it from Discord and requiring a restart. Please confirm that you'd like to commit this action.",
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

        message = await ctx.send(embed=embed)
        await message.add_reaction(emoji="✅")
        await message.add_reaction(emoji="❌")

        def check(reaction, user):
            return user == author and str(reaction.emoji) in ["✅", "❌"]

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=15, check=check)
        except asyncio.TimeoutError as e:
            await message.clear_reactions()
            await write_log(f"[Log Management]: Log upload cancelled. Prompt timed out.")
            embed = discord.Embed(
                color=discord.Color.dark_red(),
                title="📃   Log Management   📃",
                description = "Log Upload Prompt Timed Out",
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

            await message.edit(embed=embed)
        else:
            await message.clear_reactions()
            if str(reaction.emoji) == "✅":
                embed = discord.Embed(
                    color=discord.Color.green(),
                    title="📃   Log Management   📃",
                    description="Uploading logs to CloudWatch...",
                    timestamp=datetime.utcnow()
                )
                embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

                await message.edit(embed=embed)

                await write_log(f"[Log Management]: {ctx.author} initiated log upload to CloudWatch")
                fl_logger.send_to_cloudwatch()

                embed = discord.Embed(
                    color=discord.Color.green(),
                    title="📃   Log Management   📃",
                    description="Upload complete.",
                    timestamp=datetime.utcnow()
                )
                embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")
                await message.edit(embed=embed)
            else:
                embed = discord.Embed(
                    color=discord.Color.dark_red(),
                    title="📃   Log Management   📃",
                    description="Upload cancelled.",
                    timestamp=datetime.utcnow()
                )
                embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")
                await write_log(f"[Log Management]: User cancelled log upload.")
                await message.edit(embed=embed)

    @commands.command()
    @check_rank(["DEV"])
    async def show_log_cache(self, ctx, region="US/Pacific"):
        try:
            timezone = pytz.timezone(region)
        except Exception as e:
            await ctx.send(content=f"Error: {e}")
        else:
            log_events = fl_logger.log_cache
            pretty_events = []

            for event in log_events:
                timestamp = event["timestamp"]
                message = event["message"]
                time = datetime.fromtimestamp(timestamp / 1000)
                local_time = timezone.localize(time)
                line = f"[{local_time.isoformat()}]: {message}\n"
                pretty_events.append(str(line))

            description = ""
            iteration = 0
            total_iterations = math.ceil(len(pretty_events) / 19)
            print(total_iterations)
            for i in range(0,len(pretty_events)):
                description += pretty_events.pop()
                if (i % 19 == 0 and i != 0) or (i == len(pretty_events) - 1):
                    await ctx.send(content=f"```text\n{description}```")
                    # iteration += 1
                    # if iteration == 1:
                    #     embed = discord.Embed(
                    #         color=discord.Color.green(),
                    #         title="📃   Log Management   📃",
                    #         description=f"```text\n{description}```"
                    #     )
                    # elif iteration == total_iterations:
                    #     embed = discord.Embed(
                    #         color=discord.Color.green(),
                    #         description=f"```text\n{description}```",
                    #         timestamp = datetime.utcnow()
                    #     )
                    #     embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")
                    # else:
                    #     embed = discord.Embed(
                    #         color=discord.Color.green(),
                    #         description=f"```text\n{description}```",
                    #     )
                    # await ctx.send(embed=embed)
                    description = ""

        

def setup(bot):
    bot.add_cog(LogManagement(bot))