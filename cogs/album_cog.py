import discord
from discord.ext import commands
from discord import app_commands
from spotipy.exceptions import SpotifyException
from services.album_service import get_current_album
import logging
from datetime import datetime

class CurrentAlbum(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sp = bot.sp
        self.logger = logging.getLogger(__name__)

    @app_commands.command(name="current", description="Get the current album")
    async def current(self, interaction: discord.Interaction):
        """Get the current album."""
        
        await interaction.response.defer()

        album_data = get_current_album()
        if not album_data:
            await interaction.response.send_message("There is no current album.")
            return  # Stops further code execution if no current album exists
        
        album_id = album_data['album_id']

        try:
            # Query Spotify API for the album
            spotify_data = self.sp.album(album_id)
            
            # Extract album details
            album_title = spotify_data['name']
            artist_name = ", ".join(artist['name'] for artist in spotify_data['artists'])
            release_date_raw = spotify_data['release_date']
            release_date = datetime.strptime(release_date_raw, "%Y-%m-%d").strftime("%B %d, %Y")
            genres = ", ".join(spotify_data['genres']) if spotify_data['genres'] else "Not available"
            cover_url = spotify_data['images'][0]['url'] if spotify_data['images'] else None
            total_tracks = spotify_data['total_tracks']
            spotify_url = spotify_data['external_urls']['spotify']
            
            # Create the embed
            embed = discord.Embed(
                title=album_title,
                description=f"By {artist_name}",
                color=discord.Color.green(),
                url=spotify_url
            )
            embed.add_field(name="Release Date", value=release_date, inline=True)
            embed.add_field(name="Genre", value=genres, inline=True)
            embed.add_field(name="Total Tracks", value=total_tracks, inline=True)
            if cover_url:
                embed.set_image(url=cover_url)
            embed.set_footer(text="Data provided by Spotify")

            # Send the embed as a response
            await interaction.response.send_message(embed=embed)
        
        except SpotifyException as e:
            await interaction.response.send_message("There was an error retrieving the album information.")
            self.logger.error(f"Spotify API error for album ID {album_id}: {e}")
        except Exception as e:
            await interaction.response.send_message("An unexpected error occurred.")
            self.logger.error(f"Unexpected error for album ID {album_id}: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(CurrentAlbum(bot))
