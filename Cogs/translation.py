import aiohttp
import os
from discord.ext import commands

class Translation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def translate_message(self, message_text: str, target_language: str) -> str:
        async with aiohttp.ClientSession() as session:
            auth_key = os.getenv('DEEPL_AUTH_KEY')
            url = 'https://api-free.deepl.com/v2/translate'
            headers = {'Authorization': f'DeepL-Auth-Key {auth_key}', 'User-Agent': 'YourApp/1.2.3'}
            data = {'text': message_text, 'target_lang': target_language}
            async with session.post(url, headers=headers, data=data) as response:
                if response.status != 200:
                    return f"Error translating message: {response.status} {response.reason}"
                response_json = await response.json()
                return response_json['translations'][0]['text']

    @commands.slash_command(name="translate")
    async def translate(self, ctx, target_language: str, *, message_text: str):
        # Translate the message
        translated_message = await self.translate_message(message_text, target_language)

        # Send the translated message back to the user
        await ctx.response.send_message(translated_message)

def setup(bot):
    bot.add_cog(Translation(bot))