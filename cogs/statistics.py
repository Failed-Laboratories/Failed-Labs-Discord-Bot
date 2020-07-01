import discord
import flcc_dbhandler as fldb
import logging
import os
import math
import psutil
import time
from datetime import datetime, timezone
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

def truncate(number, digits):
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper

class Statistics(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #events
    @commands.Cog.listener()
    async def on_ready(self):
        await write_log(f"[System]: Statistics Cog Loaded")

    
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