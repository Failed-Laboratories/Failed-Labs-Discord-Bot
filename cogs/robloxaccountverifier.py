import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timezone

async def writeLog(message):
    print(message)
    with open(f"{datetime.date(datetime.utcnow())}.log", "a") as f:
        f.write(message + "\n")

class RobloxAccountVerifier(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        await writeLog(f"[{datetime.utcnow()}]: [System]: Roblox Account Verifier Cog Loaded")

def setup(bot):
    bot.add_cog(RobloxAccountVerifier(bot))