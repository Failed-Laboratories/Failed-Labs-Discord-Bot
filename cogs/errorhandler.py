import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timezone

async def writeLog(message):
    print(message)
    with open(f"{datetime.date(datetime.utcnow())}.log", "a") as f:
        f.write(message + "\n")

class ErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        await writeLog(f"[{datetime.utcnow()}]: [System]: Error Handler Cog Loaded")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await writeLog(f"[{ctx.message.created_at}]: [Error]: {error}")
        send_message = False
        embed = discord.Embed(
            color = discord.Color.dark_red(),
            title = ":warning: Error :warning:"
        )

        if isinstance(error, commands.MissingRequiredArgument):
            embed.add_field(name="Error Message", value="Missing Required Arguments")
            send_message = True
        
        if isinstance(error, commands.ExtensionNotLoaded):
            embed.add_field(name="Error Message", value="Extension Not Loaded")
            send_message = True

        if send_message:
            embed.set_footer(text=f"Error: \n{error}")
            await ctx.send(embed=embed, delete_after=10)

    #Commands

def setup(bot):
    bot.add_cog(ErrorHandler(bot))