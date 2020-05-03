import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="$")

@bot.event
async def on_ready():
    print(f"We have logged in as: {bot.user}")

@bot.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)

@bot.command()
async def ping(ctx):
    await ctx.send(":ping_pong: Pong!")

@bot.command()
async def addpoints(ctx, user, points):
    await ctx.send("Updated {0}'s ponts: added {1}".format(user, points))

@bot.command()
async def printconsole(ctx, *args):
    print('{} arguments: {}'.format(len(args), ', '.join(args)))

@bot.command()
async def shutdown(ctx):
    if str(ctx.author) == "tycoonlover1359#6970":
        print(f"{ctx.author} initiated shutdown.")
        await ctx.send("Shutting down...")
        await bot.logout()
    else:
        print(f"{ctx.author} attempt shutdown.")
        await ctx.send("Unauthorized")


bot.run("NjM4ODkwMjc5ODMwNjgzNjQ4.XquvhA.yoncGquaS01sKYmYkuktqNt3nxg")