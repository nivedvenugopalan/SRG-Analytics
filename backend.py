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
import sys
import time
import discord
import logging
from discord.ext import commands
from colorlog import ColoredFormatter
import mysql.connector

intents = discord.Intents.all()


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
    db_host: str = config.get('secret', 'database_host')
    db_user: str = config.get('secret', 'database_username')
    db_password: str = config.get('secret', 'database_password')
    db_name: str = config.get('secret', 'database_name')
    db_port: int = config.getint('secret', 'database_port')

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


class DataManager:
    def __init__(self) -> None:
        try:
            self.con = mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                database=db_name,
                port=db_port
            )
            self.cur = self.con.cursor(prepared=True)

        except Exception as e:
            log.critical(f"Failed to connect to database. {e}")

    def add_guild(self, guild_id: int) -> None:

        self.cur.execute(
            f"""
                CREATE TABLE IF NOT EXISTS %s (
                id INT NOT NULL AUTO_INCREMENT,
                msg_id BIGINT NOT NULL,
                msg_content TEXT,
                author_id BIGINT NOT NULL,
                epoch BIGINT NOT NULL,
                ctx_id BIGINT,
                mentions TEXT,
                PRIMARY KEY (id)
                );
            """, (str(guild_id),)
        )
        self.con.commit()

        log.info(f"Created table for guild {guild_id}")

    def add_data(self, guild_id: int, msg_id: int, msg: str, author_id: int, ctx_id: int = None, mentions: list = None):

        sql = f"INSERT INTO `{guild_id}` (msg_id, msg_content, author_id, epoch"
        sql += ", ctx_id" if ctx_id else ""
        sql += ", mentions" if mentions else ""
        sql += ") VALUES (?, ?, ?, ?"
        sql += ", ?" if ctx_id else ""
        sql += ", ?" if mentions else ""
        sql += ");"

        params = [msg_id, msg, author_id, int(time.time()) * 1000]
        if ctx_id:
            params.append(ctx_id)
        if mentions:
            params.append(str(mentions))
        try:
            self.cur.execute(
                sql,
                params
            )
        except mysql.connector.errors.InterfaceError:
            self.add_guild(guild_id)
            self.cur.execute(
                sql,
                params
            )
            

        self.con.commit()

    def add_bulk_data(self, guild_id: int, data: list):
        self.cur.executemany(
            f"INSERT INTO `{str(guild_id)}` (msg_id, msg_content, author_id, epoch, ctx_id, mentions) VALUES (?, ?, ?, ?, ?, ?);",
            data)

        self.con.commit()

    def get_all_user_messages(self, guild_id: int, user_id: int):
        self.cur.execute("SELECT * FROM ? WHERE AUTHORID=?", (guild_id, user_id))
        data = self.cur.fetchall()
        print(data)
        return data
