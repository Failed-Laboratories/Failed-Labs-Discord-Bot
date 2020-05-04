import discord
from discord.ext import commands
import os
import logging
from datetime import datetime

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('[%(asctime)s]: [%(levelname)s]: [%(name)s]: %(message)s'))
logger.addHandler(handler)

bot = commands.Bot(command_prefix="$")

async def writeLog(message):
    print(message)
    with open(f"{datetime.date(datetime.now())}.log", "a") as f:
        f.write(message + "\n")

@bot.event
async def on_ready():
    await writeLog(f"[{datetime.now()}]: [System]: Logged in as: {bot.user}")

@bot.command()
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"Lodaded Cog: {extension}")
    await writeLog(f"[{ctx.message.created_at}]: [System]: Loaded Cog: {extension}")

@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    await ctx.send(f"Unloaded Cog: {extension}")
    await writeLog(f"[{ctx.message.created_at}]: [System]: Unloaded Cog: {extension}")

@bot.command()
async def reload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"Reloaded Cog: {extension}")
    await writeLog(f"[{ctx.message.created_at}]: [System]: Reloaded Cog: {extension}")

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

@bot.command()
async def shutdown(ctx):
    if str(ctx.author) == "tycoonlover1359#6970":
        await writeLog(f"[{ctx.message.created_at}]: [System]: {ctx.author} initiated shutdown.")
        await writeLog(f"[{ctx.message.created_at}]: [System]: Shutting down...\n")
        await ctx.send("Shutting down...")
        await bot.logout()
    else:
        await writeLog(f"[{ctx.message.created_at}]: [System]: {ctx.author} attempt shutdown.")
        await ctx.send("Unauthorized")


bot.run("NjM4ODkwMjc5ODMwNjgzNjQ4.XquvhA.yoncGquaS01sKYmYkuktqNt3nxg")