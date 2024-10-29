import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import logging
from services.db_service import Database
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log"),  # Log to a file
        logging.StreamHandler()  # Also log to console
    ]
)
logger = logging.getLogger("bot")

# Set up intents
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

# Initialize the bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize database and Spotipy instance
db = Database("data/db/app.db")
auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

# Attach resources to bot
bot.db = db
bot.sp = sp

# Event handlers
@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()  # Sync all commands globally
        logger.info(f"Synced {len(synced)} commands.")
    except Exception as e:
        logger.error(f"Error syncing commands: {e}")

# Main bot function for loading cogs and starting the bot
async def main():
    async with bot:
        # Load cogs
        await bot.load_extension("cogs.album_cog")
        await bot.load_extension("cogs.submission_cog")
        await bot.load_extension("cogs.rating_cog")
        
        # Start the bot
        await bot.start(BOT_TOKEN)

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())
