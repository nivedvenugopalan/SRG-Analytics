import os
import sys

import discord
from discord.ext import commands

from logging_ import log

import configparser
config = configparser.ConfigParser()
try:
    config.read('./data/config.ini')
except Exception as e:
    log.critical(f"Failed to read config.ini. Error: {e}")
    sys.exit()

log.setLevel(config.get('general', 'log_level').strip().upper())

intents = discord.Intents.all()
intents.message_content = True


class SRGAnalyticsBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            intents=intents,
            command_prefix=config.get('discord', 'prefix'),
            application_id=config.get('secret', 'application_id')
        )

    async def on_ready(self) -> None:
        await load_cogs()

        # change presence
        await self.change_presence(activity=discord.Game(name="Made by Nived, Raj & Rayan"))

        # persistant views


bot = SRGAnalyticsBot()


async def load_cogs():
    for file in os.listdir('./cogs'):
        if file.endswith('.py'):
            await bot.load_extension(f'cogs.{file[:-3]}')

try:
    bot.run(config.get('discord', 'discord_token'))
except discord.LoginFailure:
    log.critical("Invalid Discord Token. Please check your config file.")
    sys.exit()
except Exception as err:
    log.critical(f"Error while connecting to Discord. Error: {err}")
    sys.exit()
