import discord
from discord.ext import commands

class Example(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)

def setup(bot):
    bot.add_cog(Example(bot))