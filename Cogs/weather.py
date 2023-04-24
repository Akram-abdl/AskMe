import os
import aiohttp
from datetime import datetime
from discord.ext import commands

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="weather")
    async def weather(self, ctx, city: str):
        api_key = os.getenv('OPENWEATHERMAP_API_KEY')
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['cod'] == '404':
                        await ctx.response.send_message(f"Sorry, I couldn't find weather data for {city}. Please check the city name and try again.")
                    else:
                        weather_data = {}
                        for forecast in data['list']:
                            date = datetime.fromtimestamp(forecast['dt'])
                            date_str = date.strftime('%A %d %B')
                            day = date.strftime('%Y-%m-%d')
                            if day not in weather_data:
                                weather_data[day] = {
                                    'date_str': date_str,
                                    'temp': forecast['main']['temp'],
                                    'description': forecast['weather'][0]['description'],
                                    'rain': forecast.get('rain', {}).get('3h', 0)
                                }

                        weather_report = "```md\n"
                        for info in weather_data.values():
                            weather_report += f"# {info['date_str']}:\n* Temperature: {info['temp']}°C\n* Weather: {info['description']}\n* Volume of rain: {info['rain']} mm\n\n"
                        weather_report += "```"

                        await ctx.response.send_message(f"Weather forecast for **{city}**:\n{weather_report}")
                else:
                    await ctx.response.send_message(f"Sorry, I couldn't find weather data for {city}. Please check the city name and try again.")

def setup(bot):
    bot.add_cog(Weather(bot))
