import os
from discord.ext import commands
# from models.commands import generate_aliases as ga
from models.commands import extension as ext, extension_load as ext_load, extension_unload as ext_unload, \
    extension_list as ext_list
# from functions.workhorses import generate_dicts as gen_dicts
# from models.postfixes import postfixes as pfs_dict

postfix_list = []


# root cog
class Root(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    # @commands.hybrid_command(name=ga["name"], brief=ga["brief"], help=ga["help"], aliases=ga["aliases"])
    # @commands.cooldown(1, 10, commands.BucketType.user)
    # @commands.is_owner()
    # async def generate_aliases(self, ctx: commands.Context) -> None:
    #    global postfix_list
    #    postfix_list = gen_dicts(pfs_dict)
    #    await ctx.defer(ephemeral=True)
    #    await ctx.send(f'```Postfixes aliases re-generated.\n'
    #                   f'Right now list is:\n'
    #                   f'{postfix_list}```')

    # TODO: should add checks for cog is in list
    @commands.hybrid_group(name=ext["name"], brief=ext["brief"], help=ext["help"], aliases=ext["aliases"],
                           invoke_without_command=True, with_app_command=True)
    @commands.is_owner()
    async def _extensions(self, ctx: commands.Context) -> None:
        prefix = ctx.prefix
        if ctx.invoked_subcommand is None:
            await ctx.defer(ephemeral=True)
            await ctx.send(f'Please choose: you want to list, load or unload cog.'
                           f'```{prefix}cog list```'
                           f'```{prefix}cog load```'
                           f'```{prefix}cog unload```')

    @_extensions.command(name=ext_list["name"], brief=ext_list["brief"], help=ext_list["help"],
                         aliases=ext_list["aliases"], with_app_command=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.is_owner()
    async def _ext_list(self, ctx: commands.Context) -> None:
        extension_list = []
        for extension in os.listdir("./cogs/"):
            if extension.endswith(".py") and not extension.startswith("_"):
                extension_list.append(f'cogs.{extension[:-3]}')
        await ctx.defer(ephemeral=True)
        await ctx.send(f'Available cogs list is: ```{extension_list}```')

    @_extensions.command(name=ext_load["name"], brief=ext_load["brief"], help=ext_load["help"],
                         aliases=ext_load["aliases"], with_app_command=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.is_owner()
    async def _ext_load(self, ctx: commands.Context,
                        extension: str = commands.parameter(description="Extension name")) -> None:
        try:
            await self.bot.load_extension(extension)
            await ctx.defer(ephemeral=True)
            await ctx.send(f'Cog {extension} loaded successful')
        except commands.ExtensionAlreadyLoaded:
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Extension Already Loaded**\n'
                           f'Cog {extension} loaded already.')
        except commands.ExtensionNotFound:
            prefix = ctx.prefix
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Extension Not Found**\n'
                           f'This cog does not exist. Try to list cogs before load it:'
                           f'```{prefix}cog list```')
        except commands.ExtensionFailed:
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Extension Failed**\n'
                           f'This cog can not be loaded. Internal cog error.')
        except commands.NoEntryPointError:
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**No Entry Point Error**\n'
                           f'This cog can not be loaded. Setup function does not exist.')

    @_extensions.command(name=ext_unload["name"], brief=ext_unload["brief"], help=ext_unload["help"],
                         aliases=ext_unload["aliases"], with_app_command=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.is_owner()
    async def _ext_unload(self, ctx: commands.Context,
                          extension: str = commands.parameter(description="Extension name")) -> None:
        try:
            await self.bot.unload_extension(extension)
            await ctx.defer(ephemeral=True)
            await ctx.send(f'Cog {extension} unloaded successful')
        except commands.ExtensionNotLoaded:
            prefix = ctx.prefix
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Extension Not Loaded **\n'
                           f'This cog did not loaded. Try to list cogs before unload:'
                           f'```{prefix}cog list```')
        except commands.ExtensionNotFound:
            prefix = ctx.prefix
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Extension Not Found**\n'
                           f'This cog does not exist. Try to list cogs before load it:'
                           f'```{prefix}cog list```')

    # GENERATE ALIASES ERRORS HANDLER
    # @generate_aliases.error
    # async def generate_aliases_error(self, ctx, error):
    #    if isinstance(error, commands.NotOwner):
    #         await ctx.defer(ephemeral=True)
    #        await ctx.send(f'```Sorry, but you need owner permissions to re-generate aliases.```')
    #    if isinstance(error, commands.CommandOnCooldown):
    #        await ctx.defer(ephemeral=True)
    #        await ctx.send(f'```Sorry, but this command is on cooldown.\n'
    #                       f'You can use it in {round(error.retry_after, 2)} sec.```')

    # COG COMMANDS ERRORS HANDLE
    @_ext_list.error
    async def ext_list_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Missing Permissions**\n'
                           f'Sorry, but you need bot owner permissions to manage cogs.')
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Command On Cooldown**\n'
                           f'This command is on cooldown.\n'
                           f'You can use it in {round(error.retry_after, 2)} sec.')

    @_ext_load.error
    async def ext_load_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Missing Permissions**\n'
                           f'Sorry, but you need bot owner permissions to manage cogs.')
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Command On Cooldown**\n'
                           f'This command is on cooldown.\n'
                           f'You can use it in {round(error.retry_after, 2)} sec.')

    @_ext_unload.error
    async def ext_unload_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Missing Permissions**\n'
                           f'Sorry, but you need bot owner permissions to manage cogs.')
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.defer(ephemeral=True)
            await ctx.send(f'**Command On Cooldown**\n'
                           f'This command is on cooldown.\n'
                           f'You can use it in {round(error.retry_after, 2)} sec.')


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Root(bot))
