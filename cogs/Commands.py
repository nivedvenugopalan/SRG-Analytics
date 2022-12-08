import discord.ext.commands
from discord.ext import commands
from backend import DataManager

# Importing our custom variables/functions from backend.py
from backend import log


class Commands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.manager = DataManager()

    # Use @command.Cog.listener() for an event-listener (on_message, on_ready, etc.)
    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Cog: Commands.py Loaded")

    # Use @commands.slash_command() for a slash-command
    # I recommend using only slash-commands for your bot.
    @commands.slash_command(name="harvest", description="Harvests data from a guild.")
    async def harvest(self, ctx):
        await ctx.defer()

        guild = ctx.guild
        data_list = {}

        # Iterate through all channels in the guild
        for channel in guild.channels:

            # check if channel is a text channel
            if not isinstance(channel, discord.TextChannel):
                continue

            # Iterate through all messages in the channel
            data_list[channel.name] = []
            channel = self.client.get_channel(channel.id)

            # Iterate through all messages in the channel
            async for message in channel.history(limit=None):

                data_list[channel.name].append([
                    message.id, message.content, message.author.id, message.created_at,
                    message.reference.message_id if message.reference else None,
                    str([mention.id for mention in ctx.mentions]) if ctx.mentions != [] else None
                ])

        # Add the data to the database
        for channel in data_list:
            self.manager.add_bulk_data(guild.id, data_list[channel])

        await ctx.followup.send("Harvested data from the guild.")

    @commands.slash_command(name="get_all_messages")
    async def get_all_messages(self, ctx):
        self.manager.get_all_messages(ctx.guild.id, ctx.author.id)


# The `setup` function is required for the cog to work
# Don't change anything in this function, except for the
# name of the cog (Example) to the name of your class.


def setup(client):
    # Here, `Example` is the name of the class
    client.add_cog(Commands(client))
