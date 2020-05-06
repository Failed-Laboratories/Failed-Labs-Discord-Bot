import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timezone

async def write_log(message):
    print(message)
    with open(f"./logs/cmds-{datetime.date(datetime.utcnow())}.txt", "a") as f:
        f.write(message + "\n")

class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        await write_log(f"[{datetime.utcnow()}]: [System]: Help Cog Loaded")

    #Commands
    @commands.command()
    async def help(self, ctx):

        author = ctx.message.author

        embed = discord.Embed(
            color = discord.Color.green(),
            title = ":grey_question:   Bot Help   :grey_question:",
            description = f"{author.mention} Check your DMs!"
        )

        await ctx.send(embed=embed, delete_after=3)

        embed = discord.Embed(
            color = discord.Color.green(),
            title = ":grey_question:   Bot Help   :grey_question:"
        )
        embed.set_footer(text="Failed Labs Central Command")
        #embed.add_field("")


        await author.send(embed=embed)

def setup(bot):
    bot.add_cog(Help(bot))