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
3. Create config.py file in repository directory
```console
touch config.py
```
4. Register and create app in [Discord developers portal](https://discord.com/developers/applications/)
5. Add bot token, commands prefix, path to jokes database and top.gg integration options into config.py
```console

settings = {
    'token': '<token_here>',
    'prefix': '<prefix_here>',
    'shards': '<number_of_shards_here>',
    'send_stat': <True_or_False>,
    'topgg': '<topgg_token_here>'
}

jokes_db = 'jokes.db'
admin_db = 'admin.db'
```
6. Run bot
```console
python main.py
```

## Usage
Current version of bot support next user commands:
- about: show info bot and contain few links
- stat: show statistics
- hello: bot greetings you
- help: provide short and full info about commands
- joke: post a random DnD joke
- d: single roll of single dice
- roll: roll dice of any type (example: roll 5d20 4d7 3d13)
- mod: roll dice of any type with mods (example: mod 5d20-1 d10+1 4d4+2)

Admin commands:
- prefix: manage prefix for the bot commands
  - set: set new prefix (example: prefix set !)
  - restore: restore the original prefix

## Future features
- verification ✓
- performance improvement ✓
- checks ✓
- output improvements ✓
- new d command to quick single roll ✓
- change bot prefix ✓
- non-classic dice types ✓
- suffix mechanism
- errors improvements
- help improvement
- more jokes
- secret rolls
- localization
- video guide into full bot functionality
- web-site for jokes uploads
- tests
- etc

## Known issues
- using both special dice in 1 roll cause nothing
- terra incognita
