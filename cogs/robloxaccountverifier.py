import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timezone
import random
import time

async def writeLog(message):
    print(message)
    with open(f"{datetime.date(datetime.utcnow())}.log", "a") as f:
        f.write(message + "\n")

def gen_verify_phrase():
    with open("authdict.txt") as word_list:
        words = word_list.readlines()

    for x in range (0, len(words)):
        words[x] = words[x].replace("\n", "")

    first_word = random.sample(words,1)
    auth_phrase = first_word[0]

    for x in range (0, 5):

        joiners = [" and ", " the ", " do ", " can "]
        concater = random.sample(joiners, 1)
        word = random.sample(words,1)

        new_phrase = concater[0] + word[0]
        auth_phrase += new_phrase
    
    return auth_phrase


class RobloxAccountVerifier(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        await writeLog(f"[{datetime.utcnow()}]: [System]: Roblox Account Verifier Cog Loaded")

    #Commands
    @commands.command()
    async def verify(self, ctx, r_uname:str):

        author = ctx.message.author

        if str(ctx.channel.type) != "private":

            embed = discord.Embed(
                color = discord.Color.dark_red(),
                title = ":grey_exclamation:   Roblox Account Verification   :grey_exclamation:",
                description = f"{ctx.message.author.mention} Check your DMs!"
            )

            await ctx.send(embed=embed)

        auth_code = gen_verify_phrase()

        embed = discord.Embed(
            color = discord.Color.orange(),
            title = ":globe_with_meridians:   Roblox Account Verification   :globe_with_meridians:",
            description = f"Hello **{author.name}**! Please confirm that you own the Roblox account `{r_uname}` by pasting this code into your **status**: ```{auth_code}```"
        )

        with open("verifyhelp.png", "rb") as verify_help_picture:
            picture = verify_help_picture.read()
            await author.send(embed=embed, file=picture)


def setup(bot):
    bot.add_cog(RobloxAccountVerifier(bot))