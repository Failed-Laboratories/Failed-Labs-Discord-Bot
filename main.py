import discord
from discord.ext import commands
import os
import logging
from datetime import datetime, timezone
import asyncio
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=f'./logs/discord-{datetime.date(datetime.utcnow())}.txt', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('[%(asctime)s]: [%(levelname)s]: [%(name)s]: %(message)s'))
logger.addHandler(handler)

bot = commands.Bot(command_prefix="$")
bot.remove_command("help")

async def write_log(message):
    print(message)
    with open(f"./logs/cmds-{datetime.date(datetime.utcnow())}.txt", "a") as f:
        f.write(message + "\n")

@bot.event
async def on_ready():
    await write_log(f"[{datetime.utcnow()}]: [System]: Logged in as: {bot.user}")

@bot.command()
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
async def reload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    bot.load_extension(f"cogs.{extension}")

    embed = discord.Embed(
        color = discord.Color.green(),
        title = ":white_check_mark:   Module Reload   :white_check_mark:",
        description = f"Reloaded `{extension}` Module"
    )
    embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")
    
    await ctx.send(embed=embed)

    await write_log(f"[{ctx.message.created_at}]: [System]: Reloaded Cog: {extension}")

for filename in os.listdir("./cogs"):
    if filename.endswith(".py") and not filename.endswith("_lib.py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

@bot.command()
async def shutdown(ctx):
    if str(ctx.author) == "tycoonlover1359#6970":
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

    else:

        await write_log(f"[{ctx.message.created_at}]: [System]: {ctx.author} attempt shutdown.")

        embed = discord.Embed(
            color = discord.Color.dark_red(),
            title = "Bot Shutdown",
            description = "Unauthorized."
        )
        embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")
    
        await ctx.send(embed=embed)

bot.run(os.environ["DISCORDBOTKEY"])