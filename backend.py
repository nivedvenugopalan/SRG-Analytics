#   _____  _                       _   ____        _     _______                   _       _
#  |  __ \(_)                     | | |  _ \      | |   |__   __|                 | |     | |
#  | |  | |_ ___  ___ ___  _ __ __| | | |_) | ___ | |_     | | ___ _ __ ___  _ __ | | __ _| |_ ___
#  | |  | | / __|/ __/ _ \| '__/ _` | |  _ < / _ \| __|    | |/ _ \ '_ ` _ \| '_ \| |/ _` | __/ _ \
#  | |__| | \__ \ (_| (_) | | | (_| | | |_) | (_) | |_     | |  __/ | | | | | |_) | | (_| | ||  __/
#  |_____/|_|___/\___\___/|_|  \__,_| |____/ \___/ \__|    |_|\___|_| |_| |_| .__/|_|\__,_|\__\___|
#                                                                           | |
#                                                                           |_|
#
# Welcome to Raj's Discord Bot Template
#
# This template is designed to be a starting point for your own Discord bot.
# Made by RajDave69 on GitHub.
#
#
# This is the backend.py file. Here is where you'll find all the things which are run on initialization.
# Here you'll find the client, the logger, and the config file's variables.
# If you want to import a global variable or function to multiple cogs, put it here.
# You can also add more variables to the config file and import them here.
#
#

import configparser
import sqlite3
import sys
import time

import discord
import logging
from discord.ext import commands
from colorlog import ColoredFormatter

intents = discord.Intents.default()


# Initializing the logger
def colorlogger(name: str = 'my-discord-bot') -> logging.log:
    logger = logging.getLogger(name)
    stream = logging.StreamHandler()

    stream.setFormatter(ColoredFormatter(
        "%(reset)s%(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s"))
    logger.addHandler(stream)
    return logger  # Return the logger


log = colorlogger()

# Loading config.ini
config = configparser.ConfigParser()

try:
    config.read('./data/config.ini')
except Exception as e:
    log.critical("Error reading the config.ini file. Error: " + str(e))
    sys.exit()

# Getting variables from config.ini
try:
    # Getting the variables from `[general]`
    log_level: str = config.get('general', 'log_level')
    presence: str = config.get('general', 'presence')

    # Getting the variables from `[secret]`
    discord_token: str = config.get('secret', 'discord_token')

    # Getting the variables from `[discord]`
    embed_footer: str = config.get('discord', 'embed_footer')
    embed_color: int = int(config.get('discord', 'embed_color'), base=16)
    embed_url: str = config.get('discord', 'embed_url')


except Exception as err:
    log.critical(
        "Error getting variables from the config file. Error: " + str(err))
    sys.exit()

# Set the logger's log level to the one in the config file
if log_level.upper().strip() in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
    log.setLevel(log_level.upper().strip())
else:
    log.setLevel("INFO")
    log.warning(
        f"Invalid log level `{log_level.upper().strip()}`. Defaulting to INFO.")

# Initializing the client
client = commands.Bot(intents=intents)  # Setting prefix


# Add your own functions and variables here
# Happy coding! :D


class DataManager:
    def __init__(self) -> None:
        try:
            self.con = sqlite3.connect(f"./data/data.db")
            self.cur = self.con.cursor()
        except Exception as e:
            log.critical(f"Failed to connect to database. {e}")

    def add_guild(self, guild_id: int) -> None:
        self.cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (guild_id,))
        if self.cur.fetchone() is None:
            self.cur.execute(
                """
                CREATE TABLE ?
                (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                MSGID INT   NOT NULL,
                MESSAGE TEXT    NOT NULL,
                AUTHORID INT    NOT NULL,
                EPOCH INT    NOT NULL,
                CTXID INT.
                MENTIONS TEXT);
                """, (guild_id,)
            )

            log.info(f"Created table for guild {guild_id}")

        self.con.commit()

    def add_data(self, guild_id: int, msg_id: int, msg: str, author_id: int, ctx_id: int = None, mentions: list = None):

        self.con.execute("INSERT INTO ? (MSGID, MESSAGE, AUTHORID, EPOCH, CTXID, MENTIONS) VALUES (?, ?, ?, ?, ?);",
                         (guild_id, msg_id, msg, author_id, int(time.time()) * 1000, ctx_id, mentions))

        self.con.commit()

    def add_bulk_data(self, guild_id: int, data: list):
        self.con.executemany(f"INSERT INTO {guild_id} (MSGID, MESSAGE, AUTHORID, EPOCH, CTXID, MENTIONS) VALUES (?, ?, ?, ?, ?);",
                             data)

        self.con.commit()

    def get_all_messages(self, guild_id: int, user_id: int):
        data = self.con.execute("""SELECT * FROM ?
        WHERE AUTHORID=?""", (guild_id, user_id))
        data1 = self.con.commit()
        print(data, data1)
