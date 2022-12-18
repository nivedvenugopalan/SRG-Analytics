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
import validators
import collections
from discord.ext import commands
from colorlog import ColoredFormatter
from textblob import TextBlob
import mysql.connector
import nltk

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

lemmatizer = nltk.stem.WordNetLemmatizer()
nltk.download('punkt')
try:
    stop_words = set(nltk.corpus.stopwords.words('english'))
    punkt = nltk.tokenize.punkt.PunktSentenceTokenizer()
except LookupError:
    nltk.download('stopwords')
    stop_words = set(nltk.corpus.stopwords.words('english'))

# CUSTOM STOPWORDS
stop_words.update([
    "u", "yes", "like", "lmao", "oh", "lol", "huh", "what", "wut"
])


def lemmatize(word):
    lemmatizer.lemmatize(word)


def remove_stopwords(sentence):
    tokens = nltk.tokenize.word_tokenize(sentence)
    filtered = [w for w in tokens if w not in stop_words]
    return filtered


def remove_non_alpha(sentence):
    words = [word.lower() for word in sentence.split(" ") if word.isalpha()]
    return words

def process_messages(messages):
    """Returns a list of all valid words when given a list of messages from the databse."""
    # all words from data
    words = []
    for sentence in messages:
        # if it is empty
        if sentence.strip() == "":
            continue
        # if it is a codeblock
        elif sentence[0:3] == "```" or sentence[-3:] == '```':
            continue
        # if it is a link
        elif validators.url(sentence):
            continue

        # remove non alpha
        sentence = remove_non_alpha(sentence)

        # remove stopwords
        sentence = remove_stopwords(" ".join(sentence))

        for word in sentence:
            # if it is a mention
            if sentence[0:2] == "<@":
                continue

            if word == "":
                continue

            words.append(word)
    return words


class Profile:
    def __init__(self, guild_id: int, id_: int, no_of_messages: int, top_2_words: list, net_polarity: int,
                 total_mentions: int, most_mentioned_person_id: int, total_times_mentioned: int,
                 most_mentioned_by_id: int, most_mentioned_by_id_no: int) -> None:
        self.guildID = guild_id  # to be removed in the future
        self.ID = id_

        # NLP
        self.no_of_messages = no_of_messages[0]
        self.top_2_words = top_2_words
        self.net_polarity = net_polarity

        # Mentions
        self.total_mentions = total_mentions
        self.most_mentioned_person_id = most_mentioned_person_id
        self.total_times_mentioned = total_times_mentioned
        self.most_mentioned_by_id = most_mentioned_by_id
        self.most_mentioned_by_id_no = most_mentioned_by_id_no

    def __dict__(self):
        return {
            "guildID": self.guildID,
            "ID": self.ID,
            "number_of_messages": self.no_of_messages,
            "top_2_words": self.top_2_words,
            "net_polarity": self.net_polarity,
            "total_mentions": self.total_mentions,
            "most_mentioned_person_id": self.most_mentioned_person_id,
            "total_times_mentioned": self.total_times_mentioned,
            "most_mentioned_by_id": self.most_mentioned_by_id,
            "most_mentioned_by_id_no": self.most_mentioned_by_id_no
        }

    def __str__(self):
        return str(self.__dict__())


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

    def add_data(self, guild_id: int, msg_id: int, msg: str, author_id: int, ctx_id: int = None,
                 mentions: list = None) -> None:

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

    def add_bulk_data(self, guild_id: int, data: list) -> None:
        self.cur.executemany(
            f"INSERT INTO `{str(guild_id)}` (msg_id, msg_content, author_id, epoch, ctx_id, mentions) VALUES (?, ?, ?, ?, ?, ?);",
            data)

        self.con.commit()

    def _get_all_messages(self, guild_id: int, author_id: int) -> list[str]:
        self.cur.execute(f"SELECT msg_content FROM `{str(guild_id)}` WHERE author_id=?;", (author_id,))
        messages = self.cur.fetchall()

        rtn = [str(msg[0].decode()) for msg in messages]

        log.debug(rtn[:10])
        return rtn

    def _most_used_words(self, guild_id: int, author_id: int, n: int = 2, msg_cache=None) -> list[tuple[str, int]]:
        messages = self._get_all_messages(guild_id, author_id) if msg_cache is None else msg_cache

        words = process_messages(messages)

        # get frequency of each word
        freq = collections.Counter(words)
        rtn = freq.most_common(n)

        log.debug(rtn)

        return rtn

    def _net_polarity(self, guild_id: int, author_id: int, msg_cache=None):
        messages = self._get_all_messages(guild_id, author_id) if msg_cache is None else msg_cache
        number_of_messages = len(messages)
        message = ".\n".join(messages)

        polarity = round((TextBlob(message).sentiment.polarity / number_of_messages) * 10000, 4)

        log.debug(polarity)

        return polarity

    def _total_mentions(self, guild_id: int, author_id: int):
        self.cur.execute(f"SELECT mentions FROM `{str(guild_id)}` WHERE author_id={author_id} AND ctx_id IS NULL AND mentions IS NOT NULL AND ctx_id IS NULL;")
        messages = self.cur.fetchall()
        mentions = 0
        for msg in messages:
            if list(msg)[0] is not None:
                mentions += 1

        return mentions

    def _most_mentioned_person(self, guild_id: int, author_id: int):
        self.cur.execute(
            f"SELECT mentions FROM `{str(guild_id)}` WHERE author_id={author_id} AND ctx_id IS NULL AND mentions IS NOT NULL;",)
        messages = self.cur.fetchall()

        #
        # the next list is -
        # for each message in list(messages)
        # for each item in the list(message)
        # if the id is not the author's id
        # add the id to the list

        ids = [id_[1:-1] for message in list(messages) for id_ in list(message) if id_ != author_id]
        print(ids)

        freq = collections.Counter(ids)
        return freq.most_common(1)

    def _total_times_mentioned_and_by_who(self, guild_id: int, author_id: int):
        self.cur.execute(f"SELECT author_id FROM `{guild_id}` WHERE mentions LIKE '%{author_id}%' AND ctx_id != '{author_id}';")
        ids_ = self.cur.fetchall()

        author_ids = [id_[0] for id_ in ids_]
        ctr = collections.Counter(author_ids)

        return len(author_ids), ctr.most_common(1)[0][0]

    def build_profile(self, guild_id: int, author_id: int, messages=False):
        self.cur.execute(f"SELECT COUNT(author_id) FROM `{guild_id}` WHERE author_id = '{author_id}';")

        msgs = self.cur.fetchall()[0] if messages is False else None

        mmp = self._most_mentioned_person(guild_id, author_id)
        tmmp = self._total_times_mentioned_and_by_who(guild_id, author_id)

        msg_cache = self._get_all_messages(guild_id, author_id)

        return Profile(
            guild_id,
            author_id,
            msgs,
            self._most_used_words(guild_id, author_id, 2, msg_cache=msg_cache),
            self._net_polarity(guild_id, author_id, msg_cache=msg_cache),
            self._total_mentions(guild_id, author_id),
            mmp[0][0],
            mmp[0][1],
            tmmp[1],
            tmmp[0]
        )

    ### server things
    def top_server_messages(self, guild_id: int, n: int):
        self.cur.execute("SELECT msg_content FROM `{str(guild_id)}`")
        messages = self.cur.fetchall()

        words = process_messages(messages)

        # get frequency of each word
        freq = collections.Counter(words)
        rtn = freq.most_common(n)

        log.debug(rtn)

        return rtn