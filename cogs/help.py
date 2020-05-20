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

def check_rank(acceptable_rank:list):
    async def predicate(ctx):
        rank = fldb.getUserInfo(f"{ctx.message.author.id}", "PermID")
        if rank in acceptable_rank:
            return True 
        else:
            raise commands.MissingPermissions(acceptable_rank)
    return commands.check(predicate)
    
class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        await write_log(f"[{datetime.utcnow()}]: [System]: Help Cog Loaded")

    #Commands
    @commands.group(name="help", invoke_without_command=True)
    async def help(self, ctx):
        embed = discord.Embed(
            color = discord.Color.greyple(),
            title = ":grey_question:   Help   :grey_question:"
        )
        embed.set_footer(text="Failed Labs Central Command")
        embed.add_field(name="\> Developer [4] <", value="`load`, `unload`, `reload`, `shutdown`")
        embed.add_field(name="\> Moderation [3] <", value="`kick`, `ban`, `purge`", inline=False)
        embed.add_field(name="\> Miscellaneous [1] <", value="`ping`", inline=False)
        embed.add_field(name="\> Statistics [1] <", value="`stats`", inline=False)
        embed.add_field(name="\> Verification [1] <", value="`verify`", inline=False)

        await ctx.send(embed=embed)
    
    #Developer commands
    @help.command()
    async def load(self, ctx):
        embed = discord.Embed(
            color = discord.Color.greyple(),
            title = ":grey_question:   Help   :grey_question:",
            description = "Developer Commands - `load`"
        )
        embed.set_footer(text="Failed Labs Central Command")
        embed.add_field(name="Description", value="Loads a command module (cog).")
        embed.add_field(name="Usage", value="`load <module filename>`", inline=False)
        embed.add_field(name="Required Level", value="Developer")

        await ctx.send(embed=embed)
    
    @help.command()
    async def unload(self, ctx):
        embed = discord.Embed(
            color = discord.Color.greyple(),
            title = ":grey_question:   Help   :grey_question:",
            description = "Developer Commands - `unload`"
        )
        embed.set_footer(text="Failed Labs Central Command")
        embed.add_field(name="Description", value="Unloads a command module (cog).")
        embed.add_field(name="Usage", value="`unload <module filename>`", inline=False)
        embed.add_field(name="Required Level", value="Developer")

        await ctx.send(embed=embed)

    @help.command()
    async def reload(self, ctx):
        embed = discord.Embed(
            color = discord.Color.greyple(),
            title = ":grey_question:   Help   :grey_question:",
            description = "Developer Commands - `reload`"
        )
        embed.set_footer(text="Failed Labs Central Command")
        embed.add_field(name="Description", value="Reloads a command module (cog).")
        embed.add_field(name="Usage", value="`reload <module filename>`", inline=False)
        embed.add_field(name="Required Level", value="Developer")

        await ctx.send(embed=embed)

    @help.command()
    async def shutdown(self, ctx):
        embed = discord.Embed(
            color = discord.Color.greyple(),
            title = ":grey_question:   Help   :grey_question:",
            description = "Developer Commands - `shutdown`"
        )
        embed.set_footer(text="Failed Labs Central Command")
        embed.add_field(name="Description", value="Shutsdown the bot, terminating the process gracefully.")
        embed.add_field(name="Usage", value="`shutdown`", inline=False)
        embed.add_field(name="Required Level", value="Developer")

        await ctx.send(embed=embed)

    #Moderation Commands
    @help.command()
    async def kick(self, ctx):
        embed = discord.Embed(
            color = discord.Color.greyple(),
            title = ":grey_question:   Help   :grey_question:",
            description = "Moderation Commands - `kick`"
        )
        embed.set_footer(text="Failed Labs Central Command")
        embed.add_field(name="Description", value="Kicks a user from the server.")
        embed.add_field(name="Usage", value="`kick <user (mention or ID)> [reason]`", inline=False)
        embed.add_field(name="Required Level", value="Moderator")

        await ctx.send(embed=embed)

    @help.command()
    async def ban(self, ctx):
        embed = discord.Embed(
            color = discord.Color.greyple(),
            title = ":grey_question:   Help   :grey_question:",
            description = "Moderation Commands - `ban`"
        )
        embed.set_footer(text="Failed Labs Central Command")
        embed.add_field(name="Description", value="Bans a user from the server.")
        embed.add_field(name="Usage", value="`ban <user (mention or ID)> [reason]`", inline=False)
        embed.add_field(name="Required Level", value="Administrator")

        await ctx.send(embed=embed)

    @help.command()
    async def purge(self, ctx):
        embed = discord.Embed(
            color = discord.Color.greyple(),
            title = ":grey_question:   Help   :grey_question:",
            description = "Moderation Commands - `purge`"
        )
        embed.set_footer(text="Failed Labs Central Command")
        embed.add_field(name="Description", value="Mass deletes messages from the current channel.")
        embed.add_field(name="Usage", value="`purge [amount (default is 5)]`", inline=False)
        embed.add_field(name="Required Level", value="Moderator")

        await ctx.send(embed=embed)

    #Miscellaneous Commands
    @help.command()
    async def ping(self, ctx):
        embed = discord.Embed(
            color = discord.Color.greyple(),
            title = ":grey_question:   Help   :grey_question:",
            description = "Miscellaneous Commands - `ping`"
        )
        embed.set_footer(text="Failed Labs Central Command")
        embed.add_field(name="Description", value="Returns a ping pong ball. And the bot's latency.")
        embed.add_field(name="Usage", value="`ping`", inline=False)
        embed.add_field(name="Required Level", value="Visitor")

        await ctx.send(embed=embed)
    
    #Statistics Commands
    @help.command()
    async def stats(self, ctx):
        embed = discord.Embed(
            color = discord.Color.greyple(),
            title = ":grey_question:   Help   :grey_question:",
            description = "Statistics Commands - `stats`"
        )
        embed.set_footer(text="Failed Labs Central Command")
        embed.add_field(name="Description", value="Displays the bot's current resource usage statistics.")
        embed.add_field(name="Usage", value="`stats`", inline=False)
        embed.add_field(name="Required Level", value="Visitor")

        await ctx.send(embed=embed)

    #Verification Commands
    @help.command()
    async def verify(self, ctx):
        embed = discord.Embed(
            color = discord.Color.greyple(),
            title = ":grey_question:   Help   :grey_question:",
            description = "Verification Commands - `verify`"
        )
        embed.set_footer(text="Failed Labs Central Command")
        embed.add_field(name="Description", value="Verifies ownership of a Roblox account, linking it to the current Discord user.")
        embed.add_field(name="Usage", value="`verify <Roblox username>`", inline=False)
        embed.add_field(name="Required Level", value="Visitor")

        await ctx.send(embed=embed)

    #Other commands
    @commands.command()
    async def about(self, ctx):
        author = ctx.message.author
        if str(ctx.channel.type) != "private":

            embed = discord.Embed(
                color = discord.Color.blue(),
            title = ":robot:   About Me   :robot:",
                description = f"{ctx.message.author.mention} Check your DMs!"
            )

            await ctx.send(embed=embed)

        embed = discord.Embed(
            color = discord.Color.blue(),
            title = ":robot:   About Me   :robot:",
        )
        embed.add_field(
            name="Who are you?",
            value="Hello! I am the Failed Labs Discord Bot, also known as Failed Labs Central Command. I am a custom made bot that handles everything the Failed Laboratories needs me to handle. Everything from rank management and promotion to moderation, I am made to handle it so that the adminstrators and moderators don't have to do it themselves.",
            inline=False
        )
        embed.add_field(
            name="How are you hosted?",
            value="I'm hosted on a Google Cloud Platform Cloud Compute `f1-micro` VM instance. Although this doesn't sound like it could handle very much, you'd be surprised at what it can handle, even with a fairly inexperienced coder (aka my developer) making fairly unoptimized code. Despite this, I run quite well on the GCP VM I run on, using only around 20 megabytes of RAM.",
            inline=False
        )
        embed.add_field(
            name="What else are you using?",
            value="In addition to Google Cloud Platform, I also use Amazon AWS, or Amazon Web Services. I use Amazon DynamoDB as the database service for all the databases I use to manage everything from the amount of points you have to the number of moderation incidents have occurred throughout the server as a whole. Additionally, the databases also have a custom HTTP API setup so that Failed Labs Developers can interact with the databases in game. This API is built on both Amazon API Gateway as well as Amazon Lambda, allowing the databases to have reliable, scalable, yet cost-effective API service."
        )
        embed.add_field(
            name="What are you coded in?",
            value="I'm coded in Python! Go Python! Now, why didn't my developer use JavaScript and Node, or something else like C# or C++? Quite frankly, as I've been told to tell you, it's because he wanted to use Python, so deal with it. Why don't you want to use Python?",
            inline=False
        )
        embed.add_field(
            name="Who made you?",
            value="I am coded and maintained by our wonderful Chief Operating Officer, tycoonlover1359. He learned Python just to be able to make cool things both for him and so that he could make me, the bot talking to you right now.",
            inline=False
        )
        embed.add_field(
            name="What if I have other questions?",
            value="If you have any other questions, feel free to message tycoonlover1359. (He may or may not responed...it just depends.)",
            inline=False
        )
        await author.send(embed=embed)

def setup(bot):
    bot.add_cog(Help(bot))