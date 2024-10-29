import discord
from discord.ext import commands
from discord import app_commands
from spotipy.exceptions import SpotifyException
import logging 

class Albums(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db
        self.sp = bot.sp
        self.logger = logging.getLogger(__name__)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Albums cog is ready")

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

    @app_commands.command(name="submit", description="Submit an album")
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

    @app_commands.command(name="remove", description="Remove an album")
    async def remove(self, interaction: discord.Interaction, album: str):
        self.logger.info(f"Received remove command for album ID: {album}")

        album_data = self.verify_album(album)
        if not album_data:
            await interaction.response.send_message("There was an error verifying the album. Please check the album ID or try again later.")
            return

        if album_data['album_type'] != "album":
            await interaction.response.send_message("Invalid album type. Please submit a full album, not a single or compilation.")
            return

        user_id = str(interaction.user.id)
        album_id = album_data['id']

        if not self.db.submission_exists(user_id, album_id):
            await interaction.response.send_message("You have not submitted this album.")
            return

        self.db.remove_submission(user_id, album_id)
        await interaction.response.send_message(f"Album '{album_data['name']}' by {album_data['artists'][0]['name']} has been successfully removed.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Albums(bot))
