# dice-roller-bot
![GitHub](https://img.shields.io/github/license/kreicer/dice-roller-bot?style=for-the-badge)

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
5. Add bot token, commands prefix and path to jokes database into config.py
```console

settings = {
    'token': '<token_here>',
    'prefix': '<prefix_here>'
}

dbname = 'jokes.db'
```
6. Run bot
```console
python main.py
```

## Usage
Current version of bot support next commands:
- creator: show info about me and contain few links
- hello: bot greetings you
- help: provide short and full info about commands
- joke: post a random DnD joke
- roll: roll up to 30 dice with of any type (example: roll 5d20 4d7 3d13)

Will be available soon commands:
- mod: same as roll but with modifiers (example: mod 5d20+4)
- d: single roll of single dice

## Future features
- verification
- performance improvement
- new commands
- video guide into full bot functionality