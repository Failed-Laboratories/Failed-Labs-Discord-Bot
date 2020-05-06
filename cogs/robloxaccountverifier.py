import asyncio
import discord
import io
import json
import random
import time
from datetime import datetime, timezone
from discord.ext import commands
from urllib import request

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

        do_verify = True
        r_uid = ""

        resp = request.urlopen(f"https://api.roblox.com/users/get-by-username?username={r_uname}")
        data = json.loads(resp.read().decode("UTF-8"))

        if "success" in data:

            embed = discord.Embed(
                color = discord.Color.dark_red(),
                title = ":warning:   Roblox Account Verification Error   :warning:",
                description = f"Roblox User `{r_uname}` Not Found. Please Try Again."
            )
            embed.set_footer(text="Failed Labs Central Command")

            await ctx.send(embed=embed)
            do_verify = False

        author = ctx.message.author

        if str(ctx.channel.type) != "private" and do_verify:

            embed = discord.Embed(
                color = discord.Color.blue(),
                title = ":globe_with_meridians:   Roblox Account Verification   :globe_with_meridians:",
                description = f"{ctx.message.author.mention} Check your DMs!"
            )

            await ctx.send(embed=embed)

        auth_code = gen_verify_phrase()

        if do_verify:
            r_uid = data["Id"]
            embed = discord.Embed(
                color = discord.Color.orange(),
                title = ":globe_with_meridians:   Roblox Account Verification   :globe_with_meridians:",
                description = f"Hello {author.mention}!\n\nYou will be verifying the following Roblox account: ```{r_uname}```\nGo to https://www.roblox.com/feeds/ and paste this code into your **status**: ```{auth_code}```\nDo not worry about telling me when you've finished. I will check your status automatically and rank you if I find the code above.\n\nI will indicate to you that I am still checking your status by 'typing'. If you see me stop, the prompt has timed out and you will need to run the verify command again."
            )
            embed.set_footer(text="This prompt will expire in 60 seconds.\nFailed Labs Central Command")

            resp = request.urlopen("https://cdn.glitch.com/34d846a5-187e-4fda-a891-a65b043e5995%2Fverifyhelp.png?v=1588729383987")
            verify_help_picture = discord.File(
                fp = io.BytesIO(resp.read()),
                filename = "verify_help_pic.png",
                spoiler = False
            )

            await author.send(embed=embed, file=verify_help_picture)

            verified = False
            check_status = True
            x = 0

            async with author.typing():
                while check_status and x <= 10:
                    resp = request.urlopen(f"https://users.roblox.com/v1/users/{r_uid}/status")
                    data = json.loads(resp.read().decode("UTF-8"))
                    if data["status"] == auth_code:
                        check_status = False
                        verified = True
                        break
                    x = x + 1
                    await asyncio.sleep(1)

                if verified == True:
                    embed = discord.Embed(
                        color = discord.Color.green(),
                        title = ":white_check_mark:   Roblox Account Verification   :white_check_mark:",
                        description = f"Verification of Roblox User `{r_uname}` to {author.mention} Successful!"
                    )
                    embed.set_footer(text="Failed Labs Central Command")
                elif verified == False:
                    embed = discord.Embed(
                        color = discord.Color.dark_red(),
                        title = ":x:   Roblox Account Verification   :x:",
                        description = f"Verification of Roblox User `{r_uname}` to {author.mention} Failed."
                    )
                    embed.set_footer(text="Failed Labs Central Command")
                
                await author.send(embed=embed)
                    




def setup(bot):
    bot.add_cog(RobloxAccountVerifier(bot))