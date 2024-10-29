import discord
from discord.ext import commands
from discord import app_commands
from utils.album_manager import get_current_album
import logging

class Ratings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db
        self.logger = logging.getLogger(__name__)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ratings cog is ready")

    @app_commands.command(name="rate", description="Rate the current album")
    async def rate(self, interaction: discord.Interaction, rating: float, comment: str = None):
        self.logger.info(f"Received rate command for album ID: {current_album['album_id']}")
        
        current_album = get_current_album()
        if not current_album:
            await interaction.response.send_message("No current album is set.")
            return

        album_id = current_album["album_id"]
        user_id = str(interaction.user.id)

        existing_rating = self.db.get_user_rating_for_album(user_id, album_id)
        if not existing_rating:
            self.db.add_rating(user_id, album_id, rating, comment)
            await interaction.response.send_message(f"Thank you for rating '{current_album['name']}' by {current_album['artist']} with {rating}/10.")
            return

        # If there's an existing rating, prompt to re-rate
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Re-rate", style=discord.ButtonStyle.primary, custom_id="re-rate"))
        view.add_item(discord.ui.Button(label="Cancel", style=discord.ButtonStyle.secondary, custom_id="cancel"))

        await interaction.response.send_message(
            f"You have already rated '{current_album['name']}' by {current_album['artist']} "
            f"with a rating of {existing_rating[0]}/10. Would you like to re-rate?",
            view=view
        )

        async def button_callback(interaction):
            if interaction.custom_id == "re-rate":
                self.db.update_rating(user_id, album_id, rating, comment)
                await interaction.response.send_message("Your rating has been updated.")
            elif interaction.custom_id == "cancel":
                await interaction.response.send_message("Rating update canceled.")

        for item in view.children:
            item.callback = button_callback

async def setup(bot: commands.Bot):
    await bot.add_cog(Ratings(bot))
