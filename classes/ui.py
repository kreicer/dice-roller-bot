import traceback
import discord


class Feedback(discord.ui.Modal, title="Feedback"):
    username = discord.ui.TextInput(
        label="Username",
        style=discord.TextStyle.short,
        placeholder="Username (your or any)",
        required=True,
        min_length=3,
        max_length=30,
        row=1
    )

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        traceback.print_exception(type(error), error, error.__traceback__)
        await interaction.response.send_message("Something went wrong...", ephemeral=True)
