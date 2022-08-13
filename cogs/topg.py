import discord
from discord.ext import commands

import dbl
import os
from dotenv import load_dotenv

os.path.abspath(os.path.join(r'cogs', os.pardir))

load_dotenv()
DBL_TOKEN = os.getenv('DBL_TOKEN')
webhook = os.getenv('webhook')
Auth_Pass = os.getenv('Auth_Password')


class TopGG(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, bot):
        self.bot = bot
        self.token = DBL_TOKEN 
        self.dblpy = dbl.DBLClient(self.bot, self.token, webhook_path=webhook, webhook_auth=Auth_Pass, webhook_port=5000, autopost=True) # Autopost will post guild count every 30 minutes

    async def on_guild_post(self):
        bot_channel = commands.Bot.get_channel(453674795507122176)
        await bot_channel.send('Bot count updated')

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        """An event that is called whenever someone votes for the bot on top.gg."""
        print("Received an upvote:", "\n", data, sep="")

    @commands.Cog.listener()
    async def on_dbl_test(self, data):
        """An event that is called whenever someone tests the webhook system for your bot on top.gg."""
        print("Received a test upvote:", "\n", data, sep="")



async def setup(bot):
    await bot.add_cog(TopGG(bot))