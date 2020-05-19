import asyncio
import discord
import flcc_dbhandler as fldb
import logging
import os
import set_enviro_vars as sev
import time
from datetime import datetime, timezone
from discord.ext import commands

sev.set_enviroment()

prefix = os.environ["DISCORDBOTPREFIX"]

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=f'./logs/discord-{datetime.date(datetime.utcnow())}.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('[%(asctime)s]: [%(levelname)s]: [%(name)s]: %(message)s'))
logger.addHandler(handler)

bot = commands.Bot(command_prefix=prefix)
bot.remove_command("help")

async def write_log(message):
    print(message)
    with open(f"./logs/cmds-{datetime.date(datetime.utcnow())}.log", "a") as f:
        f.write(message + "\n")

def check_rank(acceptable_rank:list):
    async def predicate(ctx):
        rank = fldb.getUserInfo(f"{ctx.message.author.id}", "PermID")
        if rank in acceptable_rank:
            return True 
        else:
            raise commands.MissingPermissions(acceptable_rank)
    return commands.check(predicate)
        
#Events
@bot.event
async def on_ready():
    await write_log(f"[{datetime.utcnow()}]: [System]: Using '{prefix}' as bot prefix")
    await write_log(f"[{datetime.utcnow()}]: [System]: Logged in as: {bot.user}")
    await bot.change_presence(activity=discord.Game(name=f"{prefix}help"))

#Commands
@bot.command()
@check_rank(["DEV"])
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")

    embed = discord.Embed(
        color = discord.Color.green(),
        title = ":white_check_mark:   Module Load   :white_check_mark:",
        description = f"Loaded `{extension}` Module"
    )
    embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")
    
    await ctx.send(embed=embed)

    await write_log(f"[{ctx.message.created_at}]: [System]: Loaded Cog: {extension}")

@bot.command()
@check_rank(["DEV"])
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")

    embed = discord.Embed(
        color = discord.Color.red(),
        title = ":negative_squared_cross_mark:   Module Unload   :negative_squared_cross_mark:",
        description = f"Unloaded `{extension}` Module"
    )
    embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")
    
    await ctx.send(embed=embed)

    await write_log(f"[{ctx.message.created_at}]: [System]: Unloaded Cog: {extension}")

@bot.command()
@check_rank(["DEV"])
async def reload(ctx, extension):
    bot.reload_extension(f"cogs.{extension}")

    embed = discord.Embed(
        color = discord.Color.green(),
        title = ":white_check_mark:   Module Reload   :white_check_mark:",
        description = f"Reloaded `{extension}` Module"
    )
    embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")
    
    await ctx.send(embed=embed)

    await write_log(f"[{ctx.message.created_at}]: [System]: Reloaded Cog: {extension}")

@bot.command()
@check_rank(["DEV"])
async def shutdown(ctx):
        await write_log(f"[{ctx.message.created_at}]: [System]: {ctx.author} initiated shutdown.")
        await write_log(f"[{ctx.message.created_at}]: [System]: Shutting down...\n")


        embed = discord.Embed(
            color = discord.Color.dark_red(),
            title = ":zzz:   Bot Shutdown   :zzz:",
            description = "Shutting down..."
        )
        embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")
    
        await ctx.send(embed=embed)

        await bot.logout()

#Cogs Loader
for filename in os.listdir("./cogs"):
    if filename.endswith(".py") and not filename.endswith("_lib.py"):
        bot.load_extension(f"cogs.{filename[:-3]}")


bot.run(os.environ["DISCORDBOTKEY"])