import asyncio
import discord
import flcc_dbhandler as fldb
import time
from datetime import datetime, timezone
from discord.ext import commands

async def write_log(message):
    print(message)
    with open(f"./logs/cmds-{datetime.date(datetime.utcnow())}.log", "a") as f:
        f.write(message + "\n")

def check_rank(acceptable_rank:list, perm_set="FL"):
    async def predicate(ctx):
        ranks = fldb.getUserInfo(f"{ctx.message.author.id}", "PermIDs")
        if perm_set in ranks and ranks[perm_set] in acceptable_rank in acceptable_rank:
            return True
        elif "GBL" in ranks and ranks["GBL"] in acceptable_rank:
            return True
        else:
            raise commands.MissingPermissions(acceptable_rank)
    return commands.check(predicate)

class Miscellaneous(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #events
    @commands.Cog.listener()
    async def on_ready(self):
        await write_log(f"[{datetime.utcnow()}]: [System]: Miscellaneous Cog Loaded")

    #Commands
    @commands.command()
    async def ping(self, ctx):

        embed = discord.Embed(
            color = discord.Color.green(),
            title = ":ping_pong:   Pong!   :ping_pong:",
            description = f"Latency: {round(self.bot.latency * 1000)} ms"
        )

        embed.set_footer(text="Failed Labs Central Command")

        await ctx.send(embed=embed)

    @commands.command()
    async def test(self, ctx, iter:int):
        embed = discord.Embed(
            color = discord.Color.green(),
            title = "Testing",
            description = iter*"█"
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def pfp(self, ctx):
        profilePic = str(ctx.message.author.avatar_url_as(static_format="jpg", size=4096))
        await ctx.send(profilePic)

    @commands.command(name="print")
    @check_rank(["DEV"])
    async def _toconsole(self, ctx):
        def checkAuthor(m):
                return m.author == ctx.message.author

        try:
            msg = await self.bot.wait_for("message", check=checkAuthor, timeout=15)
        except asyncio.TimeoutError as e:
            pass
        else:
            print(msg.attachments)

    @commands.command()
    @check_rank(["DEV"])
    async def timeout(self,ctx):
        await ctx.send(content="Timing out...")

        time.sleep(30)

        await ctx.send(content="Returning...")


def setup(bot):
    bot.add_cog(Miscellaneous(bot))