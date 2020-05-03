import discord
from discord.ext import commands
import os

bot = commands.Bot(command_prefix="$")

@bot.event
async def on_ready():
    print(f"We have logged in as: {bot.user}")

@bot.command()
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"Lodaded Cog: {extension}")
    print(f"Loaded Cog: {extension}")

@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    await ctx.send(f"Unloaded Cog: {extension}")
    print(f"Unloaded Cog: {extension}")

@bot.command()
async def reload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"Reloaded Cog: {extension}")
    print(f"Reloaded Cog: {extension}")

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

@bot.command()
async def shutdown(ctx):
    if str(ctx.author) == "tycoonlover1359#6970":
        print(f"{ctx.author} initiated shutdown.")
        await ctx.send("Shutting down...")
        await bot.logout()
    else:
        print(f"{ctx.author} attempt shutdown.")
        await ctx.send("Unauthorized")


bot.run("NjM4ODkwMjc5ODMwNjgzNjQ4.XquvhA.yoncGquaS01sKYmYkuktqNt3nxg")