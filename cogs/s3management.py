import asyncio
import aiohttp
import boto3
import discord
import os
import random
import flcc_dbhandler as fldb
from botocore.exceptions import ClientError
from datetime import datetime
from discord.ext import commands
from flcc_loghandler import CloudwatchLogger

log_group = os.environ["LOGGROUP"]
fl_logger = CloudwatchLogger(log_group)

async def write_log(message:str):
    text = fl_logger.log(message)
    print(text)

def check_rank(acceptable_rank:list, perm_set="FL"):
    async def predicate(ctx):
        ranks = fldb.getUserInfo(f"{ctx.message.author.id}", "PermIDs")
        if perm_set in ranks and ranks[perm_set] in acceptable_rank:
            return True
        elif "GBL" in ranks and ranks["GBL"] in acceptable_rank:
            return True
        else:
            raise commands.MissingPermissions(acceptable_rank)
    return commands.check(predicate)

class S3Management(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        await write_log(f"[System]: S3 Management Cog Loaded")

    #Commands
    @commands.command()
    async def download(self, ctx, *, key:str):
        embed = discord.Embed(
            color=discord.Color.orange(),
            title="📂   S3 File Management   📂",
            description=f"**File Downloader**\n\nDownloading file with key:\n```text\n{key}```",
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

        message = await ctx.send(embed=embed)

        extension = key.split(".")[-1]
        suffix = random.randint(111111,999999)
        filename = f"./tmp/download-{suffix}.{extension}"

        s3 = boto3.resource("s3", region_name="us-west-2")
        try:
            obj = s3.Object("failedlabs-bot", f"{key}")
            obj.download_file(f"{filename}")
        except ClientError as e:
            pass
        else:
            embed = discord.Embed(
                color=discord.Color.green(),
                title="📂   S3 File Management   📂",
                description=f"**File Downloader**\n\nDownload of file with key ```text\n{key}```Complete. Please check your direct messages for your download.",
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=f"{ctx.message.author} \nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

            downloaded_file = discord.File(fp=f"{filename}", filename=f"{key}")

            await message.edit(embed=embed)
            await ctx.message.author.send(content=f"```{key}```",file=downloaded_file)

            os.remove(filename)

    @commands.command()
    async def upload(self, ctx):
        embed = discord.Embed(
            color=discord.Color.orange(),
            title="📂   S3 File Management   📂",
            description=f"**File Uploader**\n\nPlease specify the object key now.",
            timestamp = datetime.utcnow()
        )
        embed.set_footer(text=f"{ctx.message.author} \nThis prompt will expire in 15 seconds.\nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

        message = await ctx.send(embed=embed)

        def checkAuthor(m):
            return m.author == ctx.message.author
        
        try:
            msg = await self.bot.wait_for("message", check=checkAuthor, timeout=15)
        except asyncio.TimeoutError as e:
            embed = discord.Embed(
                color=discord.Color.dark_red(),
                title="⚠️   S3 File Management Error   ⚠️",
                description=f"**File Uploader**\n\nPrompt timed out. Please try again.",
                timestamp = datetime.utcnow()
            )
            embed.set_footer(text="Failed Labs Central Command")

            await message.edit(embed=embed)
        else:
            key = msg.content

            embed = discord.Embed(
                color=discord.Color.orange(),
                title="📂   S3 File Management   📂",
                description="**File Uploader**\n\nPlease send the file you'd like to upload now.",
                timestamp = datetime.utcnow()
            )
            embed.set_footer(text=f"{ctx.message.author} \nThis prompt will expire in 15 seconds.\nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

            await message.edit(embed=embed)

            def checkAttachments(m):
                return m.attachments != [] and m.author == ctx.message.author

            try:
                msg = await self.bot.wait_for("message", check=checkAttachments, timeout=15)
            except asyncio.TimeoutError as e:
                embed = discord.Embed(
                    color=discord.Color.dark_red(),
                    title="⚠️   S3 File Management Error   ⚠️",
                    description=f"**File Uploader**\n\nPrompt timed out. Please try again.",
                    timestamp = datetime.utcnow()
                )
                embed.set_footer(text="Failed Labs Central Command")

                await message.edit(embed=embed)
            else:
                attachments = msg.attachments

                for file in attachments:
                    filename = file.filename
                    file_url = file.url
                    temp_filename = f"./tmp/upload-{random.randint(1111,9999)}"
                    async with aiohttp.ClientSession() as session:
                        async with session.get(file_url) as response:
                            if response.status == 200:
                                file_data = await response.text()
                                with open(f"{temp_filename}", "w+") as f:
                                    f.write(file_data.replace("\n", ""))

                embed = discord.Embed(
                    color=discord.Color.orange(),
                    title="📂   S3 File Management   📂",
                    description=f"**File Uploader**\n\nUploading file to Amazon S3 with key:\n```text\n{key}```",
                    timestamp=datetime.utcnow()
                )
                embed.set_footer(text=f"{ctx.message.author}\nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")

                await message.edit(embed=embed)
                await msg.delete()

                try:
                    s3 = boto3.resource("s3", region_name="us-west-2")
                    bucket = s3.Bucket("failedlabs-bot")
                    bucket.upload_file(f"{temp_filename}", f"{key}")
                except ClientError as e:
                    embed = discord.Embed(
                        color=discord.Color.dark_red(),
                        title="⚠️   S3 File Management Error   ⚠️",
                        description=f"**File Uploader**\n\nUpload failed: {e}",
                        timestamp = datetime.utcnow()
                    )
                    embed.set_footer(text="Failed Labs Central Command")
                else:
                    embed = discord.Embed(
                        color=discord.Color.green(),
                        title="📂   S3 File Management   📂",
                        description=f"**File Uploader**\nUpload of file key:\n```text\n{key}```Complete.",
                        timestamp=datetime.utcnow()
                    )
                    embed.set_footer(text=f"{ctx.message.author}\nFailed Labs Central Command", icon_url=f"{ctx.message.author.avatar_url}")
                finally:
                    await message.edit(embed=embed)

        os.remove(f"{temp_filename}")

def setup(bot):
    bot.add_cog(S3Management(bot))
