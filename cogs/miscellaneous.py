import discord
from discord.ext import commands
from datetime import datetime

async def writeLog(message):
    print(message)
    with open(f"{datetime.date(datetime.utcnow())}.log", "a") as f:
        f.write(message + "\n")

class Miscellaneous(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #events
    @commands.Cog.listener()
    async def on_ready(self):
        await writeLog(f"[{datetime.utcnow()}]: [System]: Miscellaneous Cog Loaded")

    #Commands
    @commands.command()
    async def ping(self, ctx):

        embed = discord.Embed(
            color = discord.Color.green(),
            title = ":ping_pong:   Pong!   :ping_pong:"
        )

        embed.set_footer(text="Failed Labs Central Command")

        await ctx.send(embed=embed)

    @commands.command()
    async def embed(self, ctx):
        embed = discord.Embed(
            color = discord.Color.green(),
            title = "User Updated",
            description = f"User {ctx.message.author.name} updated"
        )

        #embed.set_author(name="Author", icon_url="https://tycoonlover1359.keybase.pub/Profile%20Pictures/Profile%20Icon.png")
        #embed.set_image(url="https://tycoonlover1359.keybase.pub/Profile%20Pictures/Profile%20Icon.png")
        #embed.set_thumbnail(url="https://tycoonlover1359.keybase.pub/Profile%20Pictures/Profile%20Icon.png")
        #embed.add_field(name="ping", value="pong")
        #embed.set_footer("Embed Footer")

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Miscellaneous(bot))