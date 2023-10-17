## Version 2.1.0
New
- New mechanic "Shortcut" (server) - allow every server have up to 10 shortcuts for dice and roll it by shortcut name
- New command "shortcut" - allow server admins manage shortcuts on their servers: list, add, reassign and delete
- New context menu command "Text to Roll" - allow scan message on server for valid dice and roll it, if it does not break current limits
- New user Interface - from old good command line in all commands to button, modals, dropdowns and more
- New postfixes - minimum, counter, success, divisor

Improved
- almost all command got new interactive UI, was reworked a little or combined few into one
- "help" command got completely new answer
- "hello" command got new text format and colors
- "about" command now contain all info and links about the bot
- "joke" command become single point to all about jokes: get joke, tell joke, rate jokes
- "prefix" command become single point to all about prefix: get prefix, change prefix, restore prefix
- "postfix" command got completely new answer
- "roll" command got some new functions, it allow add label to roll result OR tag up to 3 members and lock it
- rework "multiplier" postfix - instead of add rolls to dice, it is allow you roll same dice x times with separate output for each time

Fixed
- many typos in text
- modifier limit bug (thx to community)
- bug with checks in pen and exp postfixes
- many code improvements
- metrics

Known Issues
- "roll" command only label or tags can be applied at same time
- old UI elements stop working after bot restart
- all another promised features will be added with next patch versions

## Version 2.0.4
New
- new postfixes - keep lowest, keep highest, multiplier
- new metrics for errors

Improved
- limit dice edges in dice metrics
- add many errors handlers

Fixed
- some typos in text

## Version 2.0.3
New
- new command "support" of "community" section send you invite to community server
- return "fate" dice

Improved
- change "powerword" command name to "postfix"
- make config more neater
- allow to configure metrics basics from config
- make some "help" command outputs richer

Fixed
- bot status

## Version 2.0.2
New
- metrics in prometheus format
- metrics for guilds, rolls and powerwords

Improved
- hello command output
- roll output now flexible
- fix few errors

## Version 2.0.1
New
- return "stat" and "about" commands, was moved into "Info" cog
- new reworked "hello" command, "Community" cog
- add new postfixes (pw): penetrate, explode, reroll

Improved
- now tasks waiting bot ready status
- code improvements
- improve error text for some errors
- improve help text and answers for some commands

Fixed
- fix "joke tell" command issue, now lang going to file with joke text

## Version 2.0.0
New
- Hybrid Commands: prefix of slash - you decide
- postfix system (Power Words)
- split code on modules (cogs)
- new regexp dice split system
- feedback command
- powerwords command
- root commands group

Improved
- core changes in roll mechanism
- one command to roll them all
- code quality improvement
- errors output improvement
- joke command split on 2: hear and tell
- more stable visual output for rolls

Fixed
- fixed impossibility use bot in threads and private messages
- fixed empty output for some errors

Known issues
- temporary remove fate and explosion dice
- temporary remove info commands group

## Version 1.1.1

Improved
- exploding dice can be rolls multiple times now

## Version 1.1.0

New
- special dice "fate" and "explode"
- new commands "d" and "stat"
- new command type "admin commands"
- new admin command "prefix", subcommands "set" and "restore"

Improved
- better rolls results output
- rework "mod" command
- more validation checks added
- improve errors output
- improve help output
- few cosmetic improve
- code refactor

Fixed
- fixed explode fate dice error
- fixed infinite explode roll with edge = 1

Known issues
- table with output can be deformed if your discord window too low on width


## Version 1.0.1

Improved
- better rolls results output
- rework "about" command
- change bot status and description
- more validation checks added
- improve errors output
- add limits for rolls, edges and modifiers
- few cosmetic improve

Fixed
- fix issue with no error on wrong "mod" command arguments
- fix issue with prefix in help command
- fix "zero mod" issue

Known issues
- table with output can be deformed if your discord window too low on width


## Version 1.0.0

New
- new command "mod"
- new code architecture
- top.gg integration (optional)
- few new jokes

Improved
- aliases for commands
- rich info in help command
- rich info in errors output
- more checks
- about command

Fixed
- some checks did not work properly
- roll with number of edges equal to 0

Known issues
- pretty of the output depends on the discord window wide and number of rolls