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
    - Amazon CloudWatch - Handles logging of all commands and general command errors. The `Discord.py` library does not log to CloudWatch, only commands done through the bot (and similar actions).
    - Amazon API Gateway - Though not used by the bot, it provides access to the bot databases to sources incompatible with the AWS SDKs.
    - AWS Lambda - Handles various functions, such as bulk rank updating and updating warn and kick counts, offloading these from the bot.
    - Amazon DynamoDB - Handles the primary databases for the both, including the moderation log and user databases.
    - Amazon S3 (Simple Storage Service) - Bulk rank update and message purge log storage, as well as backup storage for essential assets (most things found in the `files` folder). Also stores backups of command logs in Amazon CloudWatch.

# Dependencies
- `AWS Boto3 SDK` - Integration and access to AWS services.
- `Discord.py` - Python wrapper for the Discord API.