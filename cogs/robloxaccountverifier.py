import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timezone
import random
import time

async def write_log(message):
    print(message)
    with open(f"./logs/cmds-{datetime.date(datetime.utcnow())}.txt", "a") as f:
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
        await write_log(f"[{datetime.utcnow()}]: [System]: Roblox Account Verifier Cog Loaded")

    #Commands
    @commands.command()
    async def verify(self, ctx, r_uname:str):

        author = ctx.message.author

        if str(ctx.channel.type) != "private":

            embed = discord.Embed(
                color = discord.Color.dark_red(),
                title = ":globe_with_meridians:   Roblox Account Verification   :globe_with_meridians:",
                description = f"{ctx.message.author.mention} Check your DMs!"
            )

            await ctx.send(embed=embed)

        auth_code = gen_verify_phrase()

        embed = discord.Embed(
            color = discord.Color.orange(),
            title = ":globe_with_meridians:   Roblox Account Verification   :globe_with_meridians:",
            description = f"Hello {author}! Please confirm that you own the Roblox account `{r_uname}` by going to https://www.roblox.com/feeds/ and pasting this code into your **status**: ```{auth_code}```\nDo not worry about telling me when you've finished. I will check your status automatically and rank you if I find the code above."
        )
        embed.set_footer(text="This prompt will expire in 60 seconds.\nFailed Labs Central Command")

        verify_help_picture = discord.File("verifyhelp.png", "verifyhelp.png")
        await author.send(embed=embed, file=verify_help_picture)


def setup(bot):
    bot.add_cog(RobloxAccountVerifier(bot))