import discord
from discord.ext import commands
import asyncio

class Example(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Moderation Cog Loaded")

    @commands.command()
    async def kick(self, ctx, member: discord.Member, *, reason="No Reason Given"):
        #await member.kick(reason=reason)
        await ctx.send(f"`{ctx.message.author}` kicked `{member}` for `{reason}`")
        print(f"{ctx.message.author} kicked {member} for {reason}")

    @commands.command()
    async def ban(self, ctx, member: discord.Member, *, reason="No Reason Given"):
        #await member.ban(reason=reason)
        await ctx.send(f"`{ctx.message.author}` banned `{member}` for `{reason}`")
        print(f"{ctx.message.author} banned {member} for {reason}")

    @commands.command()
    async def purge(self, ctx, amount=5):
        await ctx.send(f"Purging `{amount}` messages from `{ctx.channel}`")
        print(f"Purging {amount} messages from {ctx.channel}")
        await ctx.channel.purge(limit=amount+2)
        await ctx.send(f"Purged `{amount}` messages")
        print(f"Purged {amount} messages from {ctx.channel}")
        await asyncio.sleep(3)
        await ctx.channel.purge(limit=1)


def setup(bot):
    bot.add_cog(Example(bot))