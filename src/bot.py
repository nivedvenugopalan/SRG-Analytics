import os
import discord
from discord.ext import commands

from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="•", intents=intents)


@bot.event
async def on_ready():
    print(discord.__version__)
    print("Connected to Discord!")


@bot.command()
async def test(ctx):
    print("Works")
    await ctx.reply("Works!")

bot.run(os.getenv('TOKEN'))
