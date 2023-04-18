import os
import aiohttp
from discord.ext import commands

class News(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    response.raise_for_status()

    @commands.slash_command(name="news")
    async def news(self, ctx, topic: str = None, country: str = "us"):
        # Validate the country code
        country = country.lower()
        if len(country) != 2:
            await ctx.response.send_message("Invalid country code. Please use a 2-letter ISO 3166-1 code.")
            return

        base_url = f"https://newsapi.org/v2/top-headlines?country={country}&apiKey={os.getenv('NEWS_API_KEY')}"
        url = f"{base_url}&category={topic}" if topic else base_url
        response = await self.fetch(url)
        if news_articles := response["articles"]:
            await ctx.response.send_message(f"{news_articles[0]['title']}\n{news_articles[0]['url']}")

        elif topic:
            await ctx.response.send_message(f"Sorry, no news articles were found for the topic: {topic} in country: {country.upper()}")
        else:
            await ctx.response.send_message(f"Sorry, no news articles were found for the country: {country.upper()}")

def setup(bot):
    bot.add_cog(News(bot))
