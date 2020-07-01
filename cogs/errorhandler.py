import asyncio
import discord
import json
import os
import time
from datetime import datetime, timezone
from discord.ext import commands
from flcc_loghandler import CloudwatchLogger

log_group = os.environ["LOGGROUP"]
fl_logger = CloudwatchLogger(log_group)

async def write_log(message:str):
    text = fl_logger.log(message)
    print(text)

class ErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        await write_log(f"[System]: Error Handler Cog Loaded")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        settings = {}

        with open("./files/settings.json") as f:
            settings = json.loads(f.read())

        await write_log(f"[Error]: {error}")
        send_message, set_footer, write_to_log = False, False, True
        embed = discord.Embed(
            color = discord.Color.dark_red(),
            title = "⚠️   Error   ⚠️"
        )

        if isinstance(error, commands.MissingPermissions):
            embed.add_field(name="Error Message", value="You do not have permission to use this command.")
            send_message, set_footer, write_to_log = True, False, False


        if isinstance(error, commands.MissingRequiredArgument):
            embed.add_field(name="Error Message", value="Missing Required Arguments")
            send_message, set_footer, write_to_log = True, False, False
        
        if isinstance(error, commands.ExtensionNotLoaded):
            embed.add_field(name="Error Message", value="Extension Not Loaded")
            send_message, set_footer, write_to_log = True, True, False

        if isinstance(error, commands.CommandNotFound):
            send_message, set_footer, write_to_log = False, False, False

        if send_message:
            if set_footer:
                embed.set_footer(text=f"Error: \n{error}")
            await ctx.send(embed=embed, delete_after=10)

        if write_to_log:
            log_channel_id = settings["error_log_channel"]
            log_channel = self.bot.get_channel(int(log_channel_id))
            embed = discord.Embed(
                color = discord.Color.dark_red(),
                title = "⚠️   System Error   ⚠️",
                description = f"**Error:** {error} \n**Time:** {datetime.utcnow()}",
                timestamp = datetime.utcnow()
            )
            embed.set_footer(text="Failed Labs Central Command")

            await log_channel.send(embed=embed)

    #Commands

def setup(bot):
    bot.add_cog(ErrorHandler(bot))