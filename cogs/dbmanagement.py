import asyncio
import boto3
import discord
import flcc_dbhandler as fldb
import json
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from datetime import datetime
from discord.ext import commands

dynamodb = boto3.resource("dynamodb", region_name="us-west-2")

async def write_log(message):
    print(message)
    with open(f"./logs/cmds-{datetime.date(datetime.utcnow())}.log", "a") as f:
        f.write(message + "\n")

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

def translate_name(name:str, id:str):
    tableName = ""
    table = ""
    itemID = {}
    if name in ["users"]:
        tableName = "FLCC_Users"
        table = dynamodb.Table("FLCC_Users")
        itemID = {
            "DiscordUID": str(id)
        }
    elif name in ["moderations", "modlog", "mod log"]:
        tableName = "FLCC_Moderation_Log"
        table = dynamodb.Table("FLCC_Moderation_Log")
        itemID = {
            "InfractionID": str(id)
        }
    return table, tableName, itemID
    
    

class DatabaseManagement(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        await write_log(f"[{datetime.utcnow()}]: [System]: Database Management Cog Loaded")

    #Commands
    @commands.group(name="database", invoke_without_command=True, aliases=["db"])
    @check_rank(["DEV"])
    async def database(self, ctx):
        embed = discord.Embed(
            color = discord.Color.blue(),
            title = "🖥️   Database Management   🖥️",
            timestamp = datetime.utcnow()
        )
        embed.add_field(name="FLCC_Users", value="The database containing all user information.", inline=False)
        embed.add_field(name="FLCC_Moderation_Log", value="The database containing all user moderations and moderation actions.", inline=False)
        embed.set_footer(text="Failed Labs Central Command")

        await ctx.send(embed=embed)

    @database.command()
    @check_rank(["DEV"])
    async def view(self, ctx, database:str, id:str):
        table, tableName, itemID = translate_name(database, id)

        if itemID == {}:
            embed = discord.Embed(
                color = discord.Color.dark_red(),
                title = "⚠️   Database Management Error   ⚠️",
                description = "Invalid Database",
                timestamp = datetime.utcnow()
            )
            embed.set_footer(text="Failed Labs Central Command")
            await ctx.send(embed=embed, delete_after=5)

        try:
            response = table.get_item(
                Key=itemID
            )
        except ClientError as e:
            write_log(f"[{datetime.utcnow()}]: [DynamoDB Access]: {e.response['Error']['Message']}")
        else:
            if "Item" not in response:
                embed = discord.Embed(
                    color = discord.Color.dark_red(),
                    title = "🖥️   Database Management   🖥️",
                    description = "Item Not Found",
                    timestamp = datetime.utcnow()
                )
                embed.set_footer(text="Failed Labs Central Command")
                await ctx.send(embed=embed)
            else:
                item = response["Item"]
                embed = discord.Embed(
                    color = discord.Color.green(),
                    title = "🖥️   Database Management   🖥️",
                    timestamp = datetime.utcnow()
                )
                embed.add_field(name="Table", value=f"```{tableName}```")
                embed.add_field(name="Document ID", value=f"```{id}```")
                embed.add_field(name="Document Contents", value=f"```json\n{json.dumps(item, indent=4)}```", inline=False)
                embed.set_footer(text="Failed Labs Central Command")
                await ctx.send(embed=embed)

    
    @database.command(name="set")
    @check_rank(["DEV"])
    async def setRecord(self, ctx, database:str, id:str, key:str, *, value:str):
        author = ctx.message.author
        table, tableName, itemID = translate_name(database, id)
        isTable = False

        if value.startswith("{") and value.endswith("}"):
            isTable = True
            value = json.loads(value)
        elif value.startswith("[") and value.endswith("]"):
            value = value.strip("[]").replace(",", " ").replace('"', "").split()
        elif value in ["true", "True"]:
            value = True
        elif value in ["false", "False"]:
            value = False

        if itemID != {}:
            def check(reaction, user):
                return user == author and str(reaction.emoji) in ["✅", "❌"]

            embed = discord.Embed(
                color = discord.Color.orange(),
                title = "🖥️   Database Management   🖥️",
                description = ":warning:   **WARNING**   :warning:\nThe document changes you are going to make may be difficult or impossible to reverse.\n\nPlease confirm that this is correct:",
                timestamp = datetime.utcnow()
            )
            embed.add_field(name="Table", value=f"```{tableName}```")
            embed.add_field(name="Document ID", value=f"```{id}```")
            embed.add_field(name="Key", value=f"```{key}```")
            if isTable:
                embed.add_field(name="New Value", value=f"```json\n{json.dumps(value, indent=4)}```")
            else:
                embed.add_field(name="New Value", value=f"```{value}```", inline=False)
            embed.set_footer(text="This prompt will expire in 15 seconds.\nFailed Labs Central Command")
            message = await ctx.send(embed=embed)
            await message.add_reaction(emoji="✅")
            await message.add_reaction(emoji="❌")

            commitChange = False

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=15, check=check)
            except asyncio.TimeoutError as e:
                embed = discord.Embed(
                    color = discord.Color.red(),
                    title = "🖥️   Database Management   🖥️",
                    description = "Document Change Confirmation Timed Out",
                    timestamp = datetime.utcnow()
                )
            else:
                if str(reaction.emoji) == "✅":
                    embed = discord.Embed(
                        color = discord.Color.green(),
                        title = "🖥️   Database Management   🖥️",
                        description = "Document Change Successful",
                        timestamp = datetime.utcnow()
                    )
                    commitChange = True
                else:
                    embed = discord.Embed(
                        color = discord.Color.red(),
                        title = "🖥️   Database Management   🖥️",
                        description = "Document Change Cancelled",
                        timestamp = datetime.utcnow()
                    )

            if commitChange:
                try:
                    table.update_item(
                        Key = itemID,
                        UpdateExpression = f"set {key}=:a",
                        ExpressionAttributeValues = {
                            ":a": value
                        }
                    )
                except ClientError as e:
                    write_log(f"[{datetime.utcnow()}]: [DynamoDB Access]: {e.response['Error']['Message']}")
                else:
                    pass

            embed.set_footer(text="Failed Labs Central Command")
            await message.edit(embed=embed)
    
    @database.command()
    @check_rank(["DEV"])
    async def delete(self, ctx, database: str, id:str):
        author = ctx.message.author
        table, tableName, itemID = translate_name(database, id)
        
        if itemID != {}:
            def check(reaction, user):
                return user == author and str(reaction.emoji) in ["✅", "❌"]

            embed = discord.Embed(
                color = discord.Color.orange(),
                title = "🖥️   Database Management   🖥️",
                description = ":warning:   **WARNING**   :warning:\nThe document deletion you are going to make may be difficult or impossible to reverse.\n\nPlease confirm that this is correct:",
                timestamp = datetime.utcnow()
            )
            embed.add_field(name="Table", value=f"```{tableName}```")
            embed.add_field(name="Document ID", value=f"```{id}```")
            embed.set_footer(text="This prompt will expire in 15 seconds.\nFailed Labs Central Command")
            message = await ctx.send(embed=embed)
            await message.add_reaction(emoji="✅")
            await message.add_reaction(emoji="❌")

            commitChange = False

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=15, check=check)
            except asyncio.TimeoutError as e:
                embed = discord.Embed(
                    color = discord.Color.red(),
                    title = "🖥️   Database Management   🖥️",
                    description = "Document Deletion Confirmation Timed Out",
                    timestamp = datetime.utcnow()
                )
            else:
                if str(reaction.emoji) == "✅":
                    embed = discord.Embed(
                        color = discord.Color.green(),
                        title = "🖥️   Database Management   🖥️",
                        description = "Document Deletion Successful",
                        timestamp = datetime.utcnow()
                    )
                    commitChange = True
                else:
                    embed = discord.Embed(
                        color = discord.Color.red(),
                        title = "🖥️   Database Management   🖥️",
                        description = "Document Deletion Cancelled",
                        timestamp = datetime.utcnow()
                    )

            if commitChange:
                try:
                    table.delete_item(
                        Key = itemID
                    )
                except ClientError as e:
                    write_log(f"[{datetime.utcnow()}]: [DynamoDB Access]: {e.response['Error']['Message']}")
                else:
                    pass

            embed.set_footer(text="Failed Labs Central Command")
            await message.edit(embed=embed)

    @database.command()
    @check_rank(["DEV"])
    async def create(self, ctx, database:str, id:str, *, contents:str):
        author = ctx.message.author
        table, tableName, itemID = translate_name(database, id)
        contents = json.loads("{" + contents + "}")
        embed = discord.Embed(
            color = discord.Color.orange(),
            title = "🖥️   Database Management   🖥️",
            description = "Please confirm that this is correct:"
        )
        embed.add_field(name="Table", value=f"```{tableName}```")
        embed.add_field(name="Document ID", value=f"```{id}```")
        embed.add_field(name="Conents", value=f"```json\n{json.dumps(contents, indent=4)}```", inline=False)
        embed.set_footer(text="This prompt will expire in 15 seconds.\nFailed Labs Central Command")
        message = await ctx.send(embed=embed)
        await message.add_reaction(emoji="✅")
        await message.add_reaction(emoji="❌")

        commitDocument = False

        def check(reaction, user):
            return user == author and str(reaction.emoji) in ["✅", "❌"]

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=15, check=check)
        except asyncio.TimeoutError as e:
            embed = discord.Embed(
                color = discord.Color.red(),
                title = "🖥️   Database Management   🖥️",
                description = "Document Creation Confirmation Timed Out",
                timestamp = datetime.utcnow()
            )
        else:
            if str(reaction.emoji) == "✅":
                embed = discord.Embed(
                    color = discord.Color.green(),
                    title = "🖥️   Database Management   🖥️",
                    description = "Document Creation Successful",
                    timestamp = datetime.utcnow()
                )
                commitDocument = True
            else:
                embed = discord.Embed(
                    color = discord.Color.red(),
                    title = "🖥️   Database Management   🖥️",
                    description = "Document Creation Cancelled",
                    timestamp = datetime.utcnow()
                )
        
        if commitDocument:
            item = {**itemID, **contents}
            try:
                response = table.put_item(
                    Item=item
                )
            except ClientError as e:
                    write_log(f"[{datetime.utcnow()}]: [DynamoDB Access]: {e.response['Error']['Message']}")
            else:
                pass
        
        embed.set_footer(text="Failed Labs Central Command")
        await message.edit(embed=embed)

def setup(bot):
    bot.add_cog(DatabaseManagement(bot))