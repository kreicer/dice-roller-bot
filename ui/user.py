import sqlite3
import traceback

import discord
from discord.ext import commands

from functions.checks import check_shortcut_name, check_shortcut_limit
from functions.colorizer import Colorizer
from functions.config import log_file, dev_link, db_user
from functions.generators import generate_shortcut_output, generate_shortcut_empty_output, \
    generate_me_output
from functions.postfixes import postfix_check
from functions.sql import apply_sql, select_all_sql, select_sql
from functions.workhorses import logger, split_on_dice, split_on_parts
from lang.EN.buttons import server_add_shortcut
from lang.EN.errors import sql_operational_error, bad_argument, argument_parsing_error, \
    shortcut_many_arguments
from lang.EN.ui import (server_modal_shortcut, server_modal_text_shortcut,
                        server_modal_text_shortcut_placeholder, server_modal_text_dice,
                        server_modal_text_dice_placeholder, server_selector_placeholder, server_selector_none)
from models.limits import shortcuts_limit
from models.metrics import ui_counter, ui_errors_counter
from models.regexp import parsing_regexp
from models.sql.common import (shortcut_get_all, shortcut_count, shortcut_get_dice, shortcut_update,
                               shortcut_delete_single, stat_get_dice, custom_dice_count, stat_delete,
                               shortcut_delete_all, custom_dice_delete_all)


# BUTTONS
# BUTTON "RESET STATISTICS" VIEW "STATISTICS"
class ResetStatisticsButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Reset Statistics", style=discord.ButtonStyle.gray,
                         row=2, custom_id="user-button-statistics-reset")

    async def callback(self, interaction: discord.Interaction) -> None:
        discord_id = str(interaction.user.id)
        secure_src = (discord_id,)
        execute_list = [(stat_delete, secure_src)]
        apply_sql(db_user, execute_list)
        result = "<green>Statistics data was deleted successfully<end>"
        result = Colorizer(result).colorize()
        ui_counter.labels("button", "user", "statistics_reset")
        ui_counter.labels("button", "user", "statistics_reset").inc()
        await interaction.response.edit_message(content=result, view=SuccessView())


# BUTTON "DELETE ALL" VIEW "STATISTICS"
class DeleteAllButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Delete All", style=discord.ButtonStyle.red,
                         row=2, custom_id="user-button-all-delete")

    async def callback(self, interaction: discord.Interaction) -> None:
        result = ("<red>This action will delete all data:\n"
                  "- statistics\n"
                  "- shortcuts\n"
                  "- custom dice<end>")
        result = Colorizer(result).colorize()
        ui_counter.labels("button", "user", "all_delete")
        ui_counter.labels("button", "user", "all_delete").inc()
        await interaction.response.edit_message(content=result, view=ConfirmView())


# BUTTON "BACK" VIEW "SUCCESS"
class BackButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Back", style=discord.ButtonStyle.gray,
                         row=1, custom_id="user-button-back")

    async def callback(self, interaction: discord.Interaction) -> None:
        discord_id = str(interaction.user.id)
        secure = (discord_id,)
        dice_stat = select_sql(db_user, stat_get_dice, secure)
        if dice_stat == "":
            dice_stat = 0
        shortcut_number = select_sql(db_user, shortcut_count, secure)
        if shortcut_number == "":
            shortcut_number = 0
        custom_dice_number = select_sql(db_user, custom_dice_count, secure)
        if custom_dice_number == "":
            custom_dice_number = 0
        result = generate_me_output(discord_id, dice_stat, shortcut_number, custom_dice_number)
        new_view = StatView()
        ui_counter.labels("button", "user", "back")
        ui_counter.labels("button", "user", "back").inc()
        await interaction.response.edit_message(content=result, view=new_view)


# BUTTON "CONFIRM" VIEW "CONFIRM"
class ConfirmButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Confirm", style=discord.ButtonStyle.red,
                         row=1, custom_id="user-button-confirm")

    async def callback(self, interaction: discord.Interaction) -> None:
        discord_id = str(interaction.user.id)
        secure = (discord_id,)
        execute_list = [(shortcut_delete_all, secure),
                        (custom_dice_delete_all, secure),
                        (stat_delete, secure)]
        apply_sql(db_user, execute_list)
        dice_stat = select_sql(db_user, stat_get_dice, secure)
        if dice_stat == "":
            dice_stat = 0
        shortcut_number = select_sql(db_user, shortcut_count, secure)
        if shortcut_number == "":
            shortcut_number = 0
        custom_dice_number = select_sql(db_user, custom_dice_count, secure)
        if custom_dice_number == "":
            custom_dice_number = 0
        result = generate_me_output(discord_id, dice_stat, shortcut_number, custom_dice_number)
        new_view = StatView()
        ui_counter.labels("button", "user", "back")
        ui_counter.labels("button", "user", "back").inc()
        await interaction.response.edit_message(content=result, view=new_view)


# BUTTON "ADD SHORTCUT" VIEW "SHORTCUTS"
class AddShortcutButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label=server_add_shortcut, style=discord.ButtonStyle.gray, row=3,
                         custom_id="user-button-shortcut-add")

    async def callback(self, interaction: discord.Interaction) -> None:
        modal = AddShortcut()
        ui_counter.labels("button", "shortcut", "add")
        ui_counter.labels("button", "shortcut", "add").inc()
        await interaction.response.send_modal(modal)


# SELECTOR "FOLDER" VIEW "ME"
class FolderSelector(discord.ui.Select):
    def __init__(self, placeholder: str):
        topic_list = [
            discord.SelectOption(label="Statistics", value="statistics"),
            discord.SelectOption(label="Shortcuts", value="shortcuts")
        ]
        super().__init__(custom_id="dr_user_selector_folder", placeholder=placeholder, min_values=1, max_values=1,
                         options=topic_list, row=1)

    async def callback(self, interaction: discord.Interaction) -> None:
        topic = self.values[0]
        discord_id = str(interaction.user.id)
        secure = (discord_id,)
        if topic == "shortcuts":
            shortcuts = select_all_sql(db_user, shortcut_get_all, secure)
            if shortcuts:
                shortcut_number = select_sql(db_user, shortcut_count, secure)
                result = generate_shortcut_output(shortcuts, shortcut_number, shortcuts_limit)
            else:
                result = generate_shortcut_empty_output()
            new_view = ShortcutView(str(interaction.user.id))
        else:
            dice_stat = select_sql(db_user, stat_get_dice, secure)
            if dice_stat == "":
                dice_stat = 0
            shortcut_number = select_sql(db_user, shortcut_count, secure)
            if shortcut_number == "":
                shortcut_number = 0
            custom_dice_number = select_sql(db_user, custom_dice_count, secure)
            if custom_dice_number == "":
                custom_dice_number = 0
            result = generate_me_output(discord_id, dice_stat, shortcut_number, custom_dice_number)
            new_view = StatView()

        ui_counter.labels("selector", "user", "folders")
        ui_counter.labels("selector", "user", "folders").inc()
        await interaction.response.edit_message(content=result, view=new_view)


# MODALS
class AddShortcut(discord.ui.Modal, title=server_modal_shortcut):
    shortcut = discord.ui.TextInput(
        label=server_modal_text_shortcut,
        style=discord.TextStyle.short,
        placeholder=server_modal_text_shortcut_placeholder,
        required=True,
        min_length=1,
        max_length=10,
        row=1,
        custom_id="dr_user_modal_shortcut-add_shortcut"
    )
    dice = discord.ui.TextInput(
        label=server_modal_text_dice,
        style=discord.TextStyle.short,
        placeholder=server_modal_text_dice_placeholder,
        required=True,
        min_length=1,
        max_length=50,
        row=2,
        custom_id="dr_user_modal_shortcut-add_dice"
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        # main
        shortcut_name = str(self.shortcut.value)
        shortcut_dice = str(self.dice.value)
        discord_id = str(interaction.user.id)
        secure_id = (discord_id,)
        secure_shortcut = (discord_id, shortcut_name)

        # checks
        check_shortcut_name(shortcut_name)
        list_of_dice = split_on_dice(shortcut_dice)
        for dice in list_of_dice:
            dice_parts = split_on_parts(dice, parsing_regexp)
            if dice_parts["postfix"]:
                postfix_check(dice_parts)
        shortcut_number = select_sql(db_user, shortcut_count, secure_id)
        shortcut_exist = select_sql(db_user, shortcut_get_dice, secure_shortcut)
        check_shortcut_limit(shortcut_number, shortcuts_limit, shortcut_exist)

        secure_shortcut = (discord_id, shortcut_name, shortcut_dice)
        execute_list = [(shortcut_update, secure_shortcut)]
        success = apply_sql(db_user, execute_list)
        if success:
            # main
            shortcuts = select_all_sql(db_user, shortcut_get_all, secure_id)
            shortcut_number = len(shortcuts)

            # logger
            log_txt = f"[ shortcut -> button 'add shortcut' ] New shortcut was added by {discord_id} user"
            logger(log_file, "INFO", log_txt)

            # metrics
            ui_counter.labels("modal", "shortcut", "add")
            ui_counter.labels("modal", "shortcut", "add").inc()

            # answer
            result = generate_shortcut_output(shortcuts, shortcut_number, shortcuts_limit)
            await interaction.response.edit_message(content=result, view=ShortcutView(str(interaction.user.id)))
        else:
            # logger
            log_txt = f"Failed to load database file - {db_user}"
            logger(log_file, "ERROR", log_txt)

            # answer
            text = Colorizer(sql_operational_error.format(dev_link)).colorize()
            await interaction.response.send_message(text, ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, commands.BadArgument):
            ui_errors_counter.labels("modal", "shortcut", "BadArgument")
            ui_errors_counter.labels("modal", "shortcut", "BadArgument").inc()
            error_text = error.args[0]
            text = Colorizer(bad_argument.format(error_text)).colorize()
            await interaction.response.send_message(text, ephemeral=True)
        if isinstance(error, commands.ArgumentParsingError):
            ui_errors_counter.labels("modal", "shortcut", "ArgumentParsingError")
            ui_errors_counter.labels("modal", "shortcut", "ArgumentParsingError").inc()
            error_text = error.args[0]
            text = Colorizer(argument_parsing_error.format(error_text)).colorize()
            await interaction.response.send_message(text, ephemeral=True)
        if isinstance(error, commands.TooManyArguments):
            ui_errors_counter.labels("modal", "shortcut", "TooManyArguments")
            ui_errors_counter.labels("modal", "shortcut", "TooManyArguments").inc()
            error_text = error.args[0]
            text = Colorizer(shortcut_many_arguments.format(error_text)).colorize()
            await interaction.response.send_message(text, ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)


class DeleteShortcut(discord.ui.Select):
    def __init__(self, discord_id):
        # main
        options = []
        secure = (discord_id,)
        shortcuts = select_all_sql(db_user, shortcut_get_all, secure)
        if shortcuts:
            shortcut_number = len(shortcuts)
            for shortcut, dice in shortcuts:
                options.append(discord.SelectOption(label=shortcut, value=shortcut))
        else:
            shortcut_number = 1
            options.append(discord.SelectOption(label=server_selector_none, value="none"))

        super().__init__(placeholder=server_selector_placeholder, min_values=1, max_values=shortcut_number,
                         options=options, row=2, custom_id="dr_user_select_shortcut-delete")

    async def callback(self, interaction: discord.Interaction) -> None:
        discord_id = str(interaction.user.id)
        secure_id = (discord_id,)
        shortcuts_list = self.values
        execute_list = []
        for shortcut in shortcuts_list:
            execute_list.append((shortcut_delete_single, (discord_id, shortcut)))
        success = apply_sql(db_user, execute_list)
        if success:
            # main
            shortcuts = select_all_sql(db_user, shortcut_get_all, secure_id)
            shortcut_number = len(shortcuts)

            # logger
            log_txt = f"[ shortcut -> button 'add shortcut' ] Shortcut was deleted by {discord_id} user"
            logger(log_file, "INFO", log_txt)

            # metrics
            ui_counter.labels("selector", "shortcut", "remove")
            ui_counter.labels("selector", "shortcut", "remove").inc()

            # answer
            if shortcut_number > 0:
                result = generate_shortcut_output(shortcuts, shortcut_number, shortcuts_limit)
            else:
                result = generate_shortcut_empty_output()
            await interaction.response.edit_message(content=result, view=ShortcutView(str(interaction.user.id)))
        else:
            # logger
            log_txt = f"Failed to load database file - {db_user}"
            logger(log_file, "ERROR", log_txt)

            # answer
            raise sqlite3.OperationalError


# STATISTICS VIEW
class StatView(discord.ui.View):
    def __init__(self, timeout=None):
        super().__init__(timeout=timeout)
        self.add_item(FolderSelector(placeholder="Statistics"))
        self.add_item(ResetStatisticsButton())
        self.add_item(DeleteAllButton())


# SHORTCUT VIEW
class ShortcutView(discord.ui.View):
    def __init__(self, discord_id: str, timeout=None):
        super().__init__(timeout=timeout)
        self.add_item(FolderSelector(placeholder="Shortcuts"))
        self.add_item(DeleteShortcut(discord_id))
        self.add_item(AddShortcutButton())


# CONFIRM VIEW
class ConfirmView(discord.ui.View):
    def __init__(self, timeout=None):
        super().__init__(timeout=timeout)
        self.add_item(BackButton())
        self.add_item(ConfirmButton())


# SUCCESS VIEW
class SuccessView(discord.ui.View):
    def __init__(self, timeout=None):
        super().__init__(timeout=timeout)
        self.add_item(BackButton())
