from discord.ext import commands

class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def hello(self, ctx, name: str = None):
        name = name or ctx.author.display_name
        await ctx.response.send_message(f"Hello {name}!")

def setup(bot):
    bot.add_cog(Greetings(bot))
