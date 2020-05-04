import discord
from discord.ext import commands
from datetime import datetime

async def writeLog(message):
    print(message)
    with open(f"{datetime.date(datetime.now())}.log", "a") as f:
        f.write(message + "\n")

class Miscellaneous(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #events
    @commands.Cog.listener()
    async def on_ready(self):
        await writeLog(f"[{datetime.now()}]: [System]: Miscellaneous Cog Loaded")

    #Commands
    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")

def setup(bot):
    bot.add_cog(Miscellaneous(bot))