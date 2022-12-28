import discord
from discord.ext import commands
from backend import log, DataManager


class Listeners(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        self.manager = DataManager()

    # Use @command.Cog.listener() for an event-listener (on_message, on_ready, etc.)
    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Cog: Listeners.py Loaded")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.manager.add_guild(guild.id)

    @commands.Cog.listener()
    async def on_message(self, ctx: discord.Message):
        # Ignore bot messages
        if ctx.author.bot:
            return
        c = self.manager.msg_count(ctx.guild.id, ctx.author.id)
        log.debug(f"User Messages: {c}")

        self.manager.add_data(ctx.guild.id, ctx.id, ctx.content, ctx.author.id,
                              ctx.reference.message_id if ctx.reference else None,
                              [mention.id for mention in ctx.mentions] if ctx.mentions != [] else None)

        c = self.manager.msg_count(ctx.guild.id, ctx.author.id)
        log.debug(f"User Messages after commit: {c}")

        log.debug(f"Added message {ctx.id} to database.")


def setup(client):
    client.add_cog(Listeners(client))
