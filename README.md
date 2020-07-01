# Failed Labs Discord Bot
This code is for the Failed Lababoratories (aka Failed Labs) Discord bot, known as Failed Labs Central Command.

# Current Features
- Database Management
    - Create, Read, Update, Delete (CRUD) functions
- Error Handling
    - Gracefully handles all errors, though only the following alert a normal end-user:
        - Missing permissions
        - Missing arguments
        - Unloaded cogs
        - Unknown commands
- Custom Embed Help Dialog
    - Info about each command
    - Info about the bot itself
- Moderation Commands
    - Warn
    - Kick
    - Ban
- Rank Management
    - Show own rank
    - Show other rank
- Points Management
    - Bulk st points
- Bot Statistics
    - Memory (RAM) usage
    - CPU usage
- Roblox-to-Discord Account Verification
    - Bloxlink API Integration
    - RoVer API Integration
    - Custom, Bloxlink-like verification system

# Service Integrations
The bot currently uses fhe following services to function:
- Amazon Web Services
    - [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/) - Handles logging of all commands and general command errors. The [`Discord.py`](https://discordpy.readthedocs.io/en/latest/index.html) library does not log to CloudWatch, only commands done through the bot (and similar actions).
    - [Amazon API Gateway](https://aws.amazon.com/api-gateway/) - Though not used by the bot, it provides access to the bot databases to sources incompatible with the AWS SDKs.
    - [AWS Lambda](https://aws.amazon.com/lambda/) - Handles various functions, such as bulk rank updating and updating warn and kick counts, offloading these from the bot.
    - [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) - Handles the primary databases for the both, including the moderation log and user databases.
    - [Amazon S3 (Simple Storage Service)](https://aws.amazon.com/s3/) - Bulk rank update and message purge log storage, as well as backup storage for essential assets (most things found in the `files` folder). Also stores backups of command logs in Amazon CloudWatch.

# Dependencies
- [`AWS Boto3 SDK`](https://aws.amazon.com/sdk-for-python/) - Integration and access to AWS services.
- [`Discord.py`](https://discordpy.readthedocs.io/en/latest/index.html) - Python wrapper for the Discord API.