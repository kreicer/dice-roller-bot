# dice-roller-bot

[![Discord Bots](https://top.gg/api/widget/servers/809017610111942686.svg)](https://top.gg/bot/809017610111942686)

## Installation and run
Few simple steps for bot installation:
1. Clone this repository
```console
git clone git@github.com:kreicer/dice-roller-bot.git
```
2. Go to repository directory
```console
cd dice-roller-bot
```
3. Install python requirements
```console
pip install -r requirements.txt
```
4. Create config file in repository directory
```console
touch config
```
5. Register and create app in [Discord developers portal](https://discord.com/developers/applications/)
6. Add bot token, commands prefix, path to jokes database and top.gg integration options into config.py
```console
[bot]
name = <bot_name>
version = <bot_version>
developer = <developer>
token = <token_here>
shards = <number_of_shards_here>
default_prefix = <prefix_here>
dev_link = https://discordapp.com/users/<your_discord_user_id>

[topgg]
send_stat = <True_or_False>
token = <topgg_token_here>

[metrics]
enable = <True_or_False>
port = <port_number>
python_ext = <True_or_False>

[db]
jokes_db = databases/<jokes_db_name>.db
admin_db = databases/<admin_db_name>.db

[dirs]
feedback_dir = <feedback_directory>
jokes_dir = <jokes_directory>

[logs]
log_file = <log_file_name>.log

[links]
github_link = <github_link>
topgg_link = <topgg_link>
privacy_policy = <privacy_policy_doc_link>
support = http://discord.gg/<invite_code>
```
7. Run bot
```console
python bot.py
```

## Usage
Use help command or tag bot to list all available commands and it's description.


## Future features
- help improvement
- secret rolls
- localization
- video guide into full bot functionality
- web-site for jokes uploads
- tests
- etc

## Known issues
- terra incognita
