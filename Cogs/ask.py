import os
import openai
from discord.ext import commands

class Ask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        openai.api_key = os.getenv('OPENAI_API_KEY')

    @commands.slash_command()
    async def ask(self, ctx, question: str):
        # Generate a response using OpenAI
        prompt = f"Q: {question}\nA:"

        try:
            # Call the OpenAI API asynchronously
            response = openai.Completion.create(
                engine="davinci",
                prompt=prompt,
                max_tokens=200,
                n=1,
                stop=["\n"], # Add stopping condition to avoid unnecessary content in the response
                temperature=0.7,
            )
            result = response.choices[0].text.strip()

            # Remove 'A: ' from the response
            if result.startswith('A: '):
                result = result[3:]
        except (openai.error.InvalidRequestError, ValueError, IndexError) as e:
            print(f"Exception caught: {e}")
            await ctx.response.send_message("Sorry, I couldn't generate a response. Please try again later.")
            return

        # Send the response back to the user
        await ctx.response.send_message(content=result)

def setup(bot):
    bot.add_cog(Ask(bot))
