import discord
from discord.ext import commands, tasks

from classes.ui import Feedback
from functions.workhorses import text_writer, logger, generate_info_output, generate_help_short_output, \
    generate_commands_help, generate_hello_text
from functions.config import dir_feedback, log_file, community_support, dev_github, topgg_link, community_policy
from models.commands import cmds, cogs
from models.metrics import commands_counter, errors_counter, ui_modals_counter, ui_button_counter, ui_selects_counter

guilds_number = 0


# COMMUNITY UI
class AboutView(discord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)


class SubmitFeedback(Feedback, title="Submit feedback"):
    feedback_text = discord.ui.TextInput(
        label="Feedback",
        style=discord.TextStyle.long,
        placeholder="Write your feedback text here...",
        required=True,
        min_length=10,
        max_length=3000,
        row=2
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        username = self.username.value
        feedback = self.feedback_text.value

        text = f"username: \"{username}\"\n" \
               f"feedback: \"{feedback}\"\n"
        text_writer(text, dir_feedback)

        log_txt = f"[ joke -> button 'submit joke' ] New joke was posted by {username}"
        logger(log_file, "INFO", log_txt)
        ui_modals_counter.labels("feedback", "submit")
        ui_modals_counter.labels("feedback", "submit").inc()
        await interaction.response.send_message("Thanks for your feedback!", ephemeral=True)


class HelpView(discord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)

    cmd_list = []
    for item in cmds.keys():
        if cmds[item]["enabled"]:
            cmd_list.append(item)
    options_list = []
    for item in cmd_list:
        opt = discord.SelectOption(label=cmds[item]["name"], value=item)
        options_list.append(opt)
    all = discord.SelectOption(label="List commands", value="all")
    options_list.insert(0, all)

    @discord.ui.select(placeholder="Select the command...", min_values=1, max_values=1, options=options_list)
    async def _command_selector(self, interaction: discord.Interaction, select: discord.ui.Select):
        command = select.values[0]
        if command == "all":
            result = generate_help_short_output(cogs)
        else:
            result = generate_commands_help(command)
        ui_selects_counter.labels("command", command)
        ui_selects_counter.labels("command", command).inc()
        await interaction.response.edit_message(content=result)

    @discord.ui.button(label="Submit feedback", style=discord.ButtonStyle.blurple, emoji="📝")
    async def _submit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = SubmitFeedback()
        ui_button_counter.labels("feedback", "submit")
        ui_button_counter.labels("feedback", "submit").inc()
        await interaction.response.send_modal(modal)


# COMMUNITY COG
class Community(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self._update_servers_number.start()

    def cog_unload(self):
        self._update_servers_number.cancel()

    @tasks.loop(hours=1)
    async def _update_servers_number(self):
        global guilds_number
        guilds_number = len(self.bot.guilds)
        # Logger
        log_txt = "Guild number updated, current number: " + str(guilds_number)
        logger(log_file, "INFO", log_txt)

    @_update_servers_number.before_loop
    async def _before_update_servers_number(self):
        await self.bot.wait_until_ready()

    # HELP COMMAND
    @commands.hybrid_command(name=cmds["hlp"]["name"], brief=cmds["hlp"]["brief"], aliases=cmds["hlp"]["aliases"],
                             with_app_command=True)
    @commands.bot_has_permissions(send_messages=True)
    async def _help(self, ctx: commands.Context) -> None:
        result = generate_help_short_output(cogs)

        view = HelpView()
        view.add_item(discord.ui.Button(label="Support Server", style=discord.ButtonStyle.link,
                                        url=community_support, emoji="🆘"))

        commands_counter.labels("help")
        commands_counter.labels("help").inc()

        await ctx.defer(ephemeral=True)
        await ctx.send(result, view=view)

    # ABOUT COMMAND
    @commands.hybrid_command(name=cmds["about"]["name"], brief=cmds["about"]["brief"], aliases=cmds["about"]["aliases"],
                             with_app_command=True)
    @commands.bot_has_permissions(send_messages=True)
    async def _about(self, ctx: commands.Context) -> None:

        result = generate_info_output(guilds_number)

        view = AboutView()
        view.add_item(discord.ui.Button(label="Github", style=discord.ButtonStyle.link,
                                        url=dev_github, emoji="🧑‍💻"))
        view.add_item(discord.ui.Button(label="Top.gg", style=discord.ButtonStyle.link,
                                        url=topgg_link, emoji="👍"))
        view.add_item(discord.ui.Button(label="Privacy Policy", style=discord.ButtonStyle.link,
                                        url=community_policy, emoji="🔏"))

        commands_counter.labels("about")
        commands_counter.labels("about").inc()
        await ctx.defer(ephemeral=True)
        await ctx.send(result, view=view)

    # HELLO COMMAND
    @commands.hybrid_command(name=cmds["hello"]["name"], brief=cmds["hello"]["brief"], aliases=cmds["hello"]["aliases"],
                             with_app_command=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True)
    async def _hello(self, ctx: commands.Context) -> None:
        hello_text = generate_hello_text()

        commands_counter.labels("hello")
        commands_counter.labels("hello").inc()

        await ctx.defer(ephemeral=True)
        await ctx.send(hello_text)

    # ABOUT ERRORS HANDLER
    @_about.error
    async def _about_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("about", "BotMissingPermissions")
            errors_counter.labels("about", "BotMissingPermissions").inc()
            dm = await ctx.author.create_dm()
            await dm.send(f'**Bot Missing Permissions**\n'
                          f'Dice Roller have missing permissions to answer you in this channel.\n'
                          f'You can solve it by adding rights in channel or server management section.')

    # HELP ERRORS HANDLER
    @_help.error
    async def _help_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("about", "BotMissingPermissions")
            errors_counter.labels("about", "BotMissingPermissions").inc()
            dm = await ctx.author.create_dm()
            await dm.send(f'**Bot Missing Permissions**\n'
                          f'Dice Roller have missing permissions to answer you in this channel.\n'
                          f'You can solve it by adding rights in channel or server management section.')

    # HELLO ERRORS HANDLER
    @_hello.error
    async def _hello_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            errors_counter.labels("hello", "BotMissingPermissions")
            errors_counter.labels("hello", "BotMissingPermissions").inc()
            dm = await ctx.author.create_dm()
            await dm.send(f'**Bot Missing Permissions**\n'
                          f'Dice Roller have missing permissions to answer you in this channel.\n'
                          f'You can solve it by adding rights in channel or server management section.')


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Community(bot))
