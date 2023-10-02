import sqlite3
import typing
import discord
from discord.ext import commands

from functions.checks import check_shortcut_name, check_shortcut_limit
from functions.colorizer import Colorizer
from functions.config import db_admin, log_file, bot_prefix, dev_link
from functions.generators import generate_prefix_output, generate_shortcut_output, generate_shortcut_empty_output
from functions.postfixes import postfix_check
from functions.sql import apply_sql, select_all_sql, select_sql
from functions.workhorses import logger, split_on_dice, split_on_parts
from lang.EN.buttons import server_prefix_set, server_prefix_restore, server_add_shortcut
from lang.EN.errors import missing_permissions, sql_operational_error, bad_argument, argument_parsing_error, \
    shortcut_many_arguments
from lang.EN.texts import command_prefix_output_default, command_prefix_output_new
from lang.EN.ui import server_modal_set_prefix, server_modal_text_new_prefix, server_modal_text_new_prefix_placeholder, \
    server_modal_shortcut, server_modal_text_shortcut, server_modal_text_shortcut_placeholder, server_modal_text_dice, \
    server_modal_text_dice_placeholder, server_selector_placeholder, server_selector_none
from models.limits import shortcuts_limit
from models.metrics import ui_button_counter, ui_modals_counter, errors_counter
from models.regexp import parsing_regexp
from models.sql import prefix_delete, source_update, prefix_update, shortcut_get_all, shortcut_count, shortcut_get_dice, \
    shortcut_update, shortcut_delete_single


# PREFIX UI
class PrefixView(discord.ui.View):
    def __init__(self, author: typing.Union[discord.Member, discord.User], timeout=None):
        self.author = author
        super().__init__(timeout=timeout)

    # check user click vs user spawn
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            text = Colorizer(missing_permissions).colorize()
            await interaction.response.send_message(text, ephemeral=True)
            return False
        return True

    @discord.ui.button(label=server_prefix_set, style=discord.ButtonStyle.gray, emoji="📥")
    async def _set_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # metrics
        ui_button_counter.labels("prefix", "set")
        ui_button_counter.labels("prefix", "set").inc()

        # answer
        modal = SetPrefix()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label=server_prefix_restore, style=discord.ButtonStyle.gray, emoji="📤")
    async def _restore_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # main
        discord_id = str(interaction.guild_id)
        secure = (discord_id,)
        execute_list = [(prefix_delete, secure)]
        success = apply_sql(db_admin, execute_list)
        if success:
            # logger
            log_txt = f"[ prefix -> button 'restore prefix' ] Prefix was restored on {discord_id} server"
            logger(log_file, "INFO", log_txt)

            # metrics
            ui_modals_counter.labels("prefix", "restore")
            ui_modals_counter.labels("prefix", "restore").inc()

            # answer
            result = generate_prefix_output(bot_prefix, command_prefix_output_default)
            await interaction.response.edit_message(content=result)
        else:
            # logger
            log_txt = f"Failed to load database file - {db_admin}"
            logger(log_file, "ERROR", log_txt)

            # answer
            text = Colorizer(sql_operational_error.format(dev_link)).colorize()
            await interaction.response.send_message(text, ephemeral=True)


class SetPrefix(discord.ui.Modal, title=server_modal_set_prefix):
    new_prefix = discord.ui.TextInput(
        label=server_modal_text_new_prefix,
        style=discord.TextStyle.short,
        placeholder=server_modal_text_new_prefix_placeholder,
        required=True,
        min_length=1,
        max_length=3,
        row=1
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        # main
        new_prefix = str(self.new_prefix.value)
        discord_id = str(interaction.guild_id)
        source_type = 1
        secure_src = (discord_id, source_type)
        secure_prefix = (discord_id, new_prefix)
        execute_list = [(source_update, secure_src), (prefix_update, secure_prefix)]
        success = apply_sql(db_admin, execute_list)
        if success:
            # logger
            log_txt = f"[ prefix -> button 'set prefix' ] New prefix was set on {discord_id} server"
            logger(log_file, "INFO", log_txt)

            # metrics
            ui_modals_counter.labels("prefix", "set")
            ui_modals_counter.labels("prefix", "set").inc()

            # answer
            result = generate_prefix_output(new_prefix, command_prefix_output_new)
            await interaction.response.edit_message(content=result)
        else:
            # logger
            log_txt = f"Failed to load database file - {db_admin}"
            logger(log_file, "ERROR", log_txt)

            # answer
            raise sqlite3.OperationalError

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, sqlite3.OperationalError):
            errors_counter.labels("prefix", "SQLOperationalError")
            errors_counter.labels("prefix", "SQLOperationalError").inc()
            text = Colorizer(sql_operational_error.format(dev_link)).colorize()
            await interaction.response.send_message(text, ephemeral=True)


# SHORTCUT UI
class ShortcutView(discord.ui.View):
    def __init__(self, author: typing.Union[discord.Member, discord.User], discord_id: str, timeout=None):
        self.author = author
        self.discord_id = discord_id
        super().__init__(timeout=timeout)
        self.add_item(DeleteShortcut(discord_id))

    # check user click vs user spawn
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            text = Colorizer(missing_permissions).colorize()
            await interaction.response.send_message(text, ephemeral=True)
            return False
        return True

    @discord.ui.button(label=server_add_shortcut, style=discord.ButtonStyle.gray, emoji="🔖", row=2)
    async def _add_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # metrics
        ui_button_counter.labels("shortcut", "add")
        ui_button_counter.labels("shortcut", "add").inc()

        # answer
        modal = AddShortcut()
        await interaction.response.send_modal(modal)


class AddShortcut(discord.ui.Modal, title=server_modal_shortcut):
    shortcut = discord.ui.TextInput(
        label=server_modal_text_shortcut,
        style=discord.TextStyle.short,
        placeholder=server_modal_text_shortcut_placeholder,
        required=True,
        min_length=1,
        max_length=10,
        row=1
    )
    dice = discord.ui.TextInput(
        label=server_modal_text_dice,
        style=discord.TextStyle.short,
        placeholder=server_modal_text_dice_placeholder,
        required=True,
        min_length=1,
        max_length=50,
        row=2
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        # main
        shortcut_name = str(self.shortcut.value)
        shortcut_dice = str(self.dice.value)
        discord_id = str(interaction.guild_id)
        author = interaction.user
        secure_id = (discord_id,)
        secure_shortcut = (discord_id, shortcut_name)

        # checks
        check_shortcut_name(shortcut_name)
        list_of_dice = split_on_dice(shortcut_dice)
        for dice in list_of_dice:
            dice_parts = split_on_parts(dice, parsing_regexp)
            if dice_parts["postfix"]:
                postfix_check(dice_parts)
        shortcut_number = select_sql(db_admin, shortcut_count, secure_id)
        shortcut_exist = select_sql(db_admin, shortcut_get_dice, secure_shortcut)
        check_shortcut_limit(shortcut_number, shortcuts_limit, shortcut_exist)

        source_type = 1
        secure_src = (discord_id, source_type)
        secure_shortcut = (discord_id, shortcut_name, shortcut_dice)
        execute_list = [(source_update, secure_src), (shortcut_update, secure_shortcut)]
        success = apply_sql(db_admin, execute_list)
        if success:
            # main
            shortcuts = select_all_sql(db_admin, shortcut_get_all, secure_id)
            shortcut_number = len(shortcuts)

            # logger
            log_txt = f"[ shortcut -> button 'add shortcut' ] New shortcut was added on {discord_id} server"
            logger(log_file, "INFO", log_txt)

            # metrics
            ui_modals_counter.labels("shortcut", "add")
            ui_modals_counter.labels("shortcut", "add").inc()

            # answer
            result = generate_shortcut_output(shortcuts, shortcut_number, shortcuts_limit)
            await interaction.response.edit_message(content=result, view=ShortcutView(author, discord_id))
        else:
            # logger
            log_txt = f"Failed to load database file - {db_admin}"
            logger(log_file, "ERROR", log_txt)

            # answer
            text = Colorizer(sql_operational_error.format(dev_link)).colorize()
            await interaction.response.send_message(text, ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, commands.BadArgument):
            errors_counter.labels("shortcut", "BadArgument")
            errors_counter.labels("shortcut", "BadArgument").inc()
            error_text = error.args[0]
            text = Colorizer(bad_argument.format(error_text)).colorize()
            await interaction.response.send_message(text, ephemeral=True)
        if isinstance(error, commands.ArgumentParsingError):
            errors_counter.labels("shortcut", "ArgumentParsingError")
            errors_counter.labels("shortcut", "ArgumentParsingError").inc()
            error_text = error.args[0]
            text = Colorizer(argument_parsing_error.format(error_text)).colorize()
            await interaction.response.send_message(text, ephemeral=True)
        if isinstance(error, commands.TooManyArguments):
            errors_counter.labels("shortcut", "TooManyArguments")
            errors_counter.labels("shortcut", "TooManyArguments").inc()
            error_text = error.args[0]
            text = Colorizer(shortcut_many_arguments.format(error_text)).colorize()
            await interaction.response.send_message(text, ephemeral=True)


class DeleteShortcut(discord.ui.Select):
    def __init__(self, discord_id: str):
        # main
        options = []
        secure = (discord_id,)
        shortcuts = select_all_sql(db_admin, shortcut_get_all, secure)
        if shortcuts:
            shortcut_number = len(shortcuts)
            for shortcut, dice in shortcuts:
                options.append(discord.SelectOption(label=shortcut, value=shortcut))
        else:
            shortcut_number = 1
            options.append(discord.SelectOption(label=server_selector_none, value="none"))

        super().__init__(placeholder=server_selector_placeholder, min_values=1, max_values=shortcut_number,
                         options=options, row=1)

    async def callback(self, interaction: discord.Interaction) -> None:
        discord_id = str(interaction.guild_id)
        secure_id = (discord_id,)
        author = interaction.user
        shortcuts_list = self.values
        execute_list = []
        for shortcut in shortcuts_list:
            execute_list.append((shortcut_delete_single, (discord_id, shortcut)))
        success = apply_sql(db_admin, execute_list)
        if success:
            # main
            shortcuts = select_all_sql(db_admin, shortcut_get_all, secure_id)
            shortcut_number = len(shortcuts)

            # logger
            log_txt = f"[ shortcut -> button 'add shortcut' ] Shortcut was deleted on {discord_id} server"
            logger(log_file, "INFO", log_txt)

            # metrics
            ui_modals_counter.labels("shortcut", "delete")
            ui_modals_counter.labels("shortcut", "delete").inc()

            # answer
            if shortcut_number > 0:
                result = generate_shortcut_output(shortcuts, shortcut_number, shortcuts_limit)
            else:
                result = generate_shortcut_empty_output()
            await interaction.response.edit_message(content=result, view=ShortcutView(author, discord_id))
        else:
            # logger
            log_txt = f"Failed to load database file - {db_admin}"
            logger(log_file, "ERROR", log_txt)

            # answer
            raise sqlite3.OperationalError
