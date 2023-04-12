import discord
import openai
from dotenv import load_dotenv
import os
import logging
import requests
import uuid

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

# Enable the required intents
intents = discord.Intents.all()

client = discord.Client(intents=intents)

openai.api_key = os.getenv('OPENAI_API_KEY')

last_message_timestamp = None  # define last_message_timestamp here

# Define translation function
async def translate_message(message, target_language):
    url = "https://api.cognitive.microsofttranslator.com/translate"
    querystring = {"api-version":"3.0","to":target_language}
    payload = [{'text': message}]
    headers = {
        "Ocp-Apim-Subscription-Key": os.getenv('AZURE_TRANSLATE_API_KEY'),
        "Content-type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4())
    }

    response = requests.post(url, json=payload, headers=headers, params=querystring)
    response.raise_for_status()

    response_text = response.json()[0]["translations"][0]["text"]
    return response_text

# Define joke and fun fact function
async def tell_joke_or_fact(message):
    # Use OpenAI to generate a response
    prompt = "Tell me a joke or a fun fact."
    response = openai.Completion.create(
        engine="text-curie-001",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )

    # Send the response back to the user
    await message.channel.send(response.choices[0].text.strip())

# Define news update function
async def get_news_update(message, topic):
    url = f"https://newsapi.org/v2/top-headlines?country=all&category={topic}&apiKey={os.getenv('NEWS_API_KEY')}"
    response = requests.get(url)
    response.raise_for_status()
    news_articles = response.json()["articles"]

    # Send the top news article to the user
    await message.channel.send(news_articles[0]["title"])
    await message.channel.send(news_articles[0]["url"])




async def quiz_game(message, last_message_timestamp):
    # Ask for the quiz topic
    await message.channel.send("What topic would you like the quiz to be on?")
    quiz_topic_message = await client.wait_for("message", timeout=30)
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
    await message.channel.send(f"Q: {question}\nA:")

    # Wait for the user's answer and check if it's correct
    answer = await client.wait_for("message", timeout=30)
    correct_answer = await get_quiz_answer(question, quiz_topic)
    if answer.content.lower() == correct_answer.lower():
        await message.channel.send("Correct!")
    else:
        await message.channel.send(f"Incorrect. The correct answer is: {correct_answer}.")




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


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    global last_message_timestamp

    if message.author.bot or (last_message_timestamp is not None and message.created_at <= last_message_timestamp):
        # Ignore messages sent by bots, or messages sent before the last response from the bot
        return

    if message.content.startswith('!hello'):
        # Send a greeting message
        response = 'Hello!'
        await message.channel.send(response)
        print("Sent response to !hello command")

    elif message.content.startswith('!ask'):
        # Get user's question
        question = message.content.replace('!ask', '').strip()

        # Generate a response using OpenAI
        prompt = f"Q: {question}\nA:"
        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.7,
        )

        # Send the response back to the user
        await message.channel.send(response.choices[0].text.strip())

    elif message.content.startswith('!translate'):
        # Get target language and message to be translated
        target_language, message_text = message.content.replace('!translate', '').split(';')

        # Translate the message
        translated_message = await translate_message(message_text, target_language)

        # Send the translated message back to the user
        await message.channel.send(translated_message)

    elif message.content.startswith('!joke') or message.content.startswith('!fact'):
        # Tell a joke or a fun fact
        await tell_joke_or_fact(message)

    elif message.content.startswith('!news'):
        # Get news update on a particular topic
        topic = message.content.replace('!news', '').strip()

        await get_news_update(message, topic)

    elif message.content.startswith('!quiz'):
        # Start a quiz game
        last_message_timestamp = message.created_at
        await quiz_game(message, last_message_timestamp)

client.run(os.getenv('DISCORD_TOKEN'))