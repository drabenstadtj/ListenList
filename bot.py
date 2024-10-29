import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio 
from utils.database import Database
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import logging

# Load environment variables
load_dotenv()

# Get the bot token from the environment
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to logging.DEBUG for more detailed output
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log"),  # Log to a file named bot.log
        logging.StreamHandler()  # Also log to console
    ]
)

# Initialize logging
logger = logging.getLogger("bot")

# Set up intents
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

# Initialize the bot with intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize the database (as a utility, not a cog)
db = Database("db/listenlist.db")  

# Initialize Spotipy for public data
auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

# Store parameters for the bot
bot.db = db
bot.sp = sp

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        # my_guild = discord.Object(id='1297991170202406922')  # Replace YOUR_GUILD_ID with your test server ID
        # synced = await bot.tree.sync(guild=my_guild)
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} commands.")
    except Exception as e:
        logger.error(f"Error syncing commands: {e}")

async def main():
    async with bot:
        # Load cogs asynchronously
        await bot.load_extension("cogs.albums")
        await bot.load_extension("cogs.ratings")
        await bot.start(BOT_TOKEN)

# Run the main function
asyncio.run(main())

