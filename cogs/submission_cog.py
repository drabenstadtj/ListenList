import discord
from discord.ext import commands
from discord import app_commands
from spotipy.exceptions import SpotifyException
import logging

class AlbumSelectMenu(discord.ui.View):
    def __init__(self, user_submissions, db, sp, user_id):
        super().__init__()
        self.db = db
        self.sp = sp
        self.user_id = user_id

        # Create select options with album details from Spotify
        options = []
        for submission in user_submissions:
            album_id = submission['album_id']
            try:
                album_data = self.sp.album(album_id)
                album_name = album_data['name']
                artist_name = ", ".join(artist['name'] for artist in album_data['artists'])
                options.append(discord.SelectOption(
                    label=f"{album_name} by {artist_name}",
                    value=album_id
                ))
            except SpotifyException as e:
                logging.error(f"Error fetching album data from Spotify for album ID {album_id}: {e}")
        
        # Initialize the select menu
        self.select = discord.ui.Select(
            placeholder="Select an album to remove",
            options=options,
            min_values=1,
            max_values=1
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: discord.Interaction):
        album_id = self.select.values[0]

        # Remove selected album from submissions
        if self.db.remove_submission(self.user_id, album_id):
            await interaction.response.send_message("Album successfully removed from your submissions.")
        else:
            await interaction.response.send_message("Error: Could not remove the album. Please try again.")

class Submissions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db
        self.sp = bot.sp
        self.logger = logging.getLogger(__name__)

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info("Submissions cog is ready")

    def verify_album(self, album_id):
        try:
            album = self.sp.album(album_id)
            self.logger.info(f"Successfully verified album ID: {album_id}")
            return album
        except SpotifyException as e:
            self.logger.error(f"Spotify API error for album ID {album_id}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error while verifying album ID {album_id}: {e}")
            return None

    @app_commands.command(name="submit", description="Add an album to your submissions! Enter the album’s Spotify link to submit it for the list.")
    async def submit(self, interaction: discord.Interaction, album: str):
        self.logger.info(f"Received submit command for album ID: {album}")

        album_data = self.verify_album(album)
        if not album_data:
            await interaction.response.send_message("There was an error verifying the album. Please check the album ID or try again later.")
            return

        if album_data['album_type'] != "album":
            await interaction.response.send_message("Invalid album type. Please submit a full album, not a single or compilation.")
            return

        user_id = str(interaction.user.id)
        album_id = album_data['id']

        if self.db.submission_exists(user_id, album_id):
            await interaction.response.send_message("You have already submitted this album.")
            return

        self.db.add_submission(user_id, album_id)
        await interaction.response.send_message(f"Album '{album_data['name']}' by {album_data['artists'][0]['name']} has been successfully submitted!")

    @app_commands.command(name="remove", description="Remove an album from your submissions! Select from the list.")
    async def remove(self, interaction: discord.Interaction):
        self.logger.info(f"Received remove command for user ID: {interaction.user.id}")

        # Fetch the user's submitted albums
        user_id = str(interaction.user.id)
        user_submissions = self.db.get_user_submissions(user_id)
        
        if not user_submissions:
            await interaction.response.send_message("You have no submitted albums.")
            return

        # Send the select menu to the user
        await interaction.response.send_message(
            "Please select an album to remove:",
            view=AlbumSelectMenu(user_submissions, self.db, self.sp, user_id)
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Submissions(bot))
