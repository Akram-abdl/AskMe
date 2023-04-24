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

# Load the cogs by looping through the Cogs folder
for filename in os.listdir('./Cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'Cogs.{filename[:-3]}')

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))
