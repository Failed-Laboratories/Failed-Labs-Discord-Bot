import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timezone

async def writeLog(message):
    print(message)
    with open(f"{datetime.date(datetime.utcnow())}.log", "a") as f:
        f.write(message + "\n")

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        await writeLog(f"[{datetime.utcnow()}]: [System]: Moderation Cog Loaded")

    #Commands
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No Reason Given"):

        embed = discord.Embed(
            color = discord.Color.orange(),
            title = ":boot:   Kicked   :boot:"
        )
        embed.add_field(name="Reason", value=f"{reason}")
        embed.set_author(name=f"{member}", icon_url=f"{member.avatar_url}")
        embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

        #await member.kick(reason=reason)

        await ctx.send(embed=embed)
        await writeLog(f"[{ctx.message.created_at}]: [Moderation]: {ctx.message.author} kicked {member} for {reason}")

    @commands.command()
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No Reason Given"):

        embed = discord.Embed(
            color = discord.Color.dark_red(),
            title = ":no_entry:   Banned   :no_entry:"
        )
        embed.add_field(name="Reason", value=f"{reason}")
        embed.set_author(name=f"{member}", icon_url=f"{member.avatar_url}")
        embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

        #await member.ban(reason=reason)

        await ctx.send(embed=embed)
        await writeLog(f"[{ctx.message.created_at}]: [Moderation]: {ctx.message.author} banned {member} for {reason}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount=5):

        embed = discord.Embed(
            color = discord.Color.orange(),
            title = ":arrows_counterclockwise:   Message Purge   :arrows_counterclockwise:",
            description = f"Purging {amount} Messages..."
        )
        embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")
        
        await ctx.send(embed=embed)
        await writeLog(f"[{ctx.message.created_at}]: [Moderation]: Purging {amount} messages from {ctx.channel}")
        await asyncio.sleep(1)
        await ctx.channel.purge(limit=amount+2)

        embed = discord.Embed(
            color = discord.Color.green(),
            title = ":white_check_mark:   Message Purge   :white_check_mark:",
            description = f"Purged {amount} Messages"
        )
        embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

        await ctx.send(embed=embed, delete_after=5)

        await writeLog(f"[{ctx.message.created_at}]: [Moderation]: {ctx.message.author} purged {amount} messages from {ctx.channel}")

def setup(bot):
    bot.add_cog(Moderation(bot))
    bot.remove_command("help")