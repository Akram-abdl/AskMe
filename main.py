import asyncio
import aiohttp
import discord
import openai
from dotenv import load_dotenv
import os
import logging
import requests
import uuid
from discord.ext import commands
import json
from urllib.parse import urlencode

# # add debug 
logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv()

# Enable the required intents
intents = discord.Intents.all()

# Create the bot instance with a prefix and enabled intents
bot = commands.Bot(command_prefix='/', intents=intents)

# Load the cogs
bot.load_extension('Cogs.greetings')
bot.load_extension('Cogs.fun')
bot.load_extension('Cogs.news')
bot.load_extension('Cogs.translation')
bot.load_extension('Cogs.ask')

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))
