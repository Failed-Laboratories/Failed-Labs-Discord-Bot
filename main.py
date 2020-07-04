import set_enviro_vars as sev
sev.set_enviroment()

import asyncio
import discord
import flcc_dbhandler as fldb
import logging
import os
import time
from datetime import datetime
from discord.ext import commands
from flcc_loghandler import CloudwatchLogger

prefix = os.environ["DISCORDBOTPREFIX"]
log_group = os.environ["LOGGROUP"]

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=f'./logs/discord-{datetime.date(datetime.utcnow())}.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('[%(asctime)s]: [%(levelname)s]: [%(name)s]: %(message)s'))
logger.addHandler(handler)

fl_logger = CloudwatchLogger(log_group)
write_log = fl_logger.log

bot = commands.Bot(command_prefix=prefix)
bot.remove_command("help")

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
        
#Events
@bot.event
async def on_ready():
    print(write_log(f"[System]: Using AWS Profile '{os.environ['AWS_Profile']}'"))
    print(write_log(f"[System]: Using '{prefix}' as bot prefix"))
    print(write_log(f"[System]: Logged in as: {bot.user}"))
    await bot.change_presence(activity=discord.Game(name=f"{prefix}help"))

#Commands
@bot.command()
@check_rank(["DEV"])
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")

    embed = discord.Embed(
        color = discord.Color.green(),
        title = ":white_check_mark:   Module Load   :white_check_mark:",
        description = f"Loaded `{extension}` Module",
        timestamp = datetime.utcnow()
    )
    embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")
    
    await ctx.send(embed=embed)

    print(write_log(f"[System]: Loaded Cog: {extension}"))

@bot.command()
@check_rank(["DEV"])
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")

    embed = discord.Embed(
        color = discord.Color.red(),
        title = ":negative_squared_cross_mark:   Module Unload   :negative_squared_cross_mark:",
        description = f"Unloaded `{extension}` Module",
        timestamp = datetime.utcnow()
    )
    embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")
    
    await ctx.send(embed=embed)

    print(write_log(f"[System]: Unloaded Cog: {extension}"))

@bot.command()
@check_rank(["DEV"])
async def reload(ctx, extension):
    bot.reload_extension(f"cogs.{extension}")

    embed = discord.Embed(
        color = discord.Color.green(),
        title = ":white_check_mark:   Module Reload   :white_check_mark:",
        description = f"Reloaded `{extension}` Module",
        timestamp = datetime.utcnow()
    )
    embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")
    
    await ctx.send(embed=embed)

    print(write_log(f"[System]: Reloaded Cog: {extension}"))

@bot.command()
@check_rank(["DEV"])
async def shutdown(ctx):
        print(write_log(f"[System]: {ctx.author} initiated shutdown."))
        print(write_log(f"[System]: Shutting down..."))


        embed = discord.Embed(
            color = discord.Color.dark_red(),
            title = ":zzz:   Bot Shutdown   :zzz:",
            description = "Shutting down...",
            timestamp = datetime.utcnow()
        )
        embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")
    
        await ctx.send(embed=embed)

        print(write_log(f"[System]: Deleting files in ./tmp..."))

        for item in os.listdir("./tmp"):
            print(write_log(f"[System]: Deleting './tmp/{item}'..."))
            os.remove(f"./tmp/{item}")
    
        print(write_log(f"[System]: Logging out..."))
        print(write_log(f"[System]: Sending logs to Cloudwatch..."))
        #fl_logger.send_to_cloudwatch()

        await bot.logout()

#Cogs Loader
for filename in os.listdir("./cogs"):
    if filename.endswith(".py") and not filename.startswith("dne_"):
        bot.load_extension(f"cogs.{filename[:-3]}")


bot.run(os.environ["DISCORDBOTKEY"])