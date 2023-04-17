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

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

# Enable the required intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
openai.api_key = os.getenv('OPENAI_API_KEY')

last_message_timestamp = None  # define last_message_timestamp here

@bot.command(name="hello")
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author}!")

# Define translation function
async def translate_message(message_text: str, target_language: str) -> str:
    async with aiohttp.ClientSession() as session:
        auth_key = os.getenv('DEEPL_AUTH_KEY')
        url = f'https://api-free.deepl.com/v2/translate'
        headers = {'Authorization': f'DeepL-Auth-Key {auth_key}', 'User-Agent': 'YourApp/1.2.3'}
        data = {'text': message_text, 'target_lang': target_language}
        async with session.post(url, headers=headers, data=data) as response:
            if response.status == 200:
                response_json = await response.json()
                translated_text = response_json['translations'][0]['text']
                return translated_text
            else:
                return f"Error translating message: {response.status} {response.reason}"



@bot.command(name="translate")
async def translate(ctx, target_language: str, *, message_text: str):
    # Translate the message
    translated_message = await translate_message(message_text, target_language)

    # Send the translated message back to the user
    await ctx.send(translated_message)

# Define joke and fun fact function
@bot.command(name="joke")
async def joke(ctx):
    # Use OpenAI to generate a response
    prompt = "Tell me a joke."
    response = openai.Completion.create(
        engine="text-curie-001",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )

    # Send the response back to the user
    await ctx.send(response.choices[0].text.strip())

@bot.command(name="fact")
async def fact(ctx):
    # Use OpenAI to generate a response
    prompt = "Tell me a fun fact."
    response = openai.Completion.create(
        engine="text-curie-001",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )

    # Send the response back to the user
    await ctx.send(response.choices[0].text.strip())

# Define news update function
@bot.command(name="news")
async def news(ctx, topic):
    url = f"https://newsapi.org/v2/top-headlines?country=all&category={topic}&apiKey={os.getenv('NEWS_API_KEY')}"
    response = requests.get(url)
    response.raise_for_status()
    news_articles = response.json()["articles"]

    # Send the top news article to the user
    await ctx.send(news_articles[0]["title"])
    await ctx.send(news_articles[0]["url"])


async def quiz_game(ctx, last_message_timestamp):
    # Ask for the quiz topic
    await ctx.send("What topic would you like the quiz to be on?")
    quiz_topic_message = await bot.wait_for("message", check=lambda m: m.author == ctx.author, timeout=30)
    quiz_topic = quiz_topic_message.content

    # Generate a quiz question on the given topic
    prompt = f"Generate a quiz question on the topic of {quiz_topic}."
    response = openai.Completion.create(
        engine="text-curie-001",
        prompt=prompt,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.7,
    )

    # Send the quiz question to the user
    question = response.choices[0].text.strip()
    await ctx.send(f"Q: {question}\nA:")

    # Wait for the user's answer and check if it's correct
    answer = await bot.wait_for("message", check=lambda m: m.author == ctx.author, timeout=30)
    correct_answer = await get_quiz_answer(question, quiz_topic)
    if answer.content.lower() == correct_answer.lower():
        await ctx.send("Correct!")
    else:
        await ctx.send(f"Incorrect. The correct answer is: {correct_answer}.")

async def get_quiz_answer(question, quiz_topic):
    url = f"https://api.openai.com/v1/answers/{quiz_topic.lower()}?model=curie&question={question}&examples_context=To+help+you+answer+the+question%2C+here+are+a+few+examples+of+possible+answers.&examples=5"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    answer = response.json()["answers"][0]

    return answer

@bot.command(name="quiz")
async def quiz(ctx):
    global last_message_timestamp
    last_message_timestamp = ctx.message.created_at

    await quiz_game(ctx, last_message_timestamp)


# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))