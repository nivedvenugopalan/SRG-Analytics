import os
import discord
from discord.ext import commands

# token stuff
import dotenv
dotenv.load_dotenv()
token = str(os.getenv("TOKEN"))

intents = discord.Intents.all()
client = commands.Bot(intents=intents)

# cogs
client.load_extension('cogs.processMessages')


@client.event
async def on_ready():
    print(f"The bot is online.")


client.run(token)
