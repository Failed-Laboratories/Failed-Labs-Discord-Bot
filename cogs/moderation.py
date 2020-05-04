import discord
from discord.ext import commands
import asyncio
from datetime import datetime

async def writeLog(message):
    print(message)
    with open(f"{datetime.date(datetime.now())}.log", "a") as f:
        f.write(message + "\n")

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        await writeLog(f"[{datetime.now()}]: [System]: Moderation Cog Loaded")

    #Commands
    @commands.command()
    async def kick(self, ctx, member: discord.Member, *, reason="No Reason Given"):
        await member.kick(reason=reason)
        await ctx.send(f"`{ctx.message.author}` kicked `{member}` for `{reason}`")
        await writeLog(f"[{ctx.message.created_at}]: [Moderation]: {ctx.message.author} kicked {member} for {reason}")

    @commands.command()
    async def ban(self, ctx, member: discord.Member, *, reason="No Reason Given"):
        await member.ban(reason=reason)
        await ctx.send(f"`{ctx.message.author}` banned `{member}` for `{reason}`")
        await writeLog(f"[{ctx.message.created_at}]: [Moderation]: {ctx.message.author} banned {member} for {reason}")

    @commands.command()
    async def purge(self, ctx, amount=5):
        await ctx.send(f"Purging `{amount}` messages from `{ctx.channel}`")
        await writeLog(f"[{ctx.message.created_at}]: [Moderation]: Purging {amount} messages from {ctx.channel}")
        await ctx.channel.purge(limit=amount+2)
        message = await ctx.send(f"`{ctx.message.author}` purged `{amount}` messages")
        await writeLog(f"[{ctx.message.created_at}]: [Moderation]: {ctx.message.author} purged {amount} messages from {ctx.channel}")
        await asyncio.sleep(3)
        await message.delete()


def setup(bot):
    bot.add_cog(Moderation(bot))