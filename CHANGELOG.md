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