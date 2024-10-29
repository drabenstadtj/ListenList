import discord
from discord.ext import commands
from discord import app_commands
from services.album_service import get_current_album
import logging

class RatingModal(discord.ui.Modal, title="Rate this Week's Album"):
    rating = discord.ui.TextInput(
        label="Rating", 
        style=discord.TextStyle.short,
        placeholder="Enter your rating here (1-10).",
    )
    comment = discord.ui.TextInput(
        label="Comment",
        style=discord.TextStyle.paragraph,
        max_length=500,
        placeholder="Enter some comments about this week's album."
    )

    def __init__(self, current_album, db, logger):
        super().__init__()
        self.current_album = current_album
        self.db = db
        self.logger = logger

    async def on_submit(self, interaction: discord.Interaction):
        self.logger.info(f"Received rating submission for album ID: {self.current_album['album_id']}")

        rating = float(self.rating.value)  # Convert to float
        comment = self.comment.value

        existing_rating = self.db.get_user_rating_for_album(interaction.user.id, self.current_album['album_id'])
        if not existing_rating:
            self.db.add_rating(interaction.user.id, self.current_album['album_id'], rating, comment)
            await interaction.response.send_message(
                f"Thank you for rating '{self.current_album['name']}' by {self.current_album['artist']} with {rating}/10."
            )
        else:
            # If rating exists, update it
            self.db.update_rating(interaction.user.id, self.current_album['album_id'], rating, comment)
            await interaction.response.send_message("Your rating has been updated.")

class Ratings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db
        self.logger = logging.getLogger(__name__)

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info("Ratings cog is ready")

    @app_commands.command(name="rate", description="Rate the current album")
    async def rate(self, interaction: discord.Interaction):
        self.logger.info("Received rate command")

        current_album = get_current_album()
        if not current_album:
            await interaction.response.send_message("No current album is set.")
            return

        # Check if user has already rated the album
        existing_rating = self.db.get_user_rating_for_album(interaction.user.id, current_album["album_id"])
        if not existing_rating:
            # No existing rating, send the modal
            await interaction.response.send_modal(RatingModal(current_album, self.db, self.logger))
        else:
            # Existing rating, ask to update
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="Re-rate", style=discord.ButtonStyle.primary, custom_id="re-rate"))
            view.add_item(discord.ui.Button(label="Cancel", style=discord.ButtonStyle.secondary, custom_id="cancel"))

            await interaction.response.send_message(
                f"You have already rated '{current_album['name']}' by {current_album['artist']} "
                f"with a rating of {existing_rating[0]}/10.0. Would you like to re-rate?",
                view=view
            )

            async def button_callback(interaction: discord.Interaction):
                # Access the button's custom_id from the interaction data
                if interaction.data["custom_id"] == "re-rate":
                    await interaction.response.send_modal(RatingModal(current_album, self.db, self.logger))
                elif interaction.data["custom_id"] == "cancel":
                    await interaction.response.send_message("Rating update canceled.")

            # Set callback for each button in the view
            for item in view.children:
                item.callback = button_callback

async def setup(bot: commands.Bot):
    await bot.add_cog(Ratings(bot))
