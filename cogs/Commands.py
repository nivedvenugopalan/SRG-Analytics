import time

import discord.ext.commands
from discord.ext import commands
from backend import DataManager

# Importing our custom variables/functions from backend.py
from backend import log


class Commands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.manager = DataManager()
        self.count = 0

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
        start_time = time.time()

        cmd_channel = self.client.get_channel(ctx.channel.id)

        async def harvest_channel(channel):
            # Iterate through all messages in the channel
            async for message in channel.history(limit=None):
                data_list[channel.name].append([
                    message.id, message.content, message.author.id, message.created_at,
                    message.reference.message_id if message.reference else None,
                    str([mention.id for mention in message.mentions]) if message.mentions != [] else None
                ])
                self.count += 1
                if self.count % 1000 == 0:
                    print(self.count)

        # Iterate through all channels in the guild
        for channel in guild.channels:

            # check if channel is a text channel
            if not isinstance(channel, discord.TextChannel):
                continue

            # Iterate through all messages in the channel
            data_list[channel.name] = []
            channel = self.client.get_channel(channel.id)
            log.info(f"Harvesting channel {channel.name}...")
            try:
                await cmd_channel.send(f"Harvesting channel {channel.name}...")
            except Exception as err:
                log.error(err)

            await harvest_channel(channel)

        # Add the data to the database
        for channel in data_list:
            print(channel)
            self.manager.add_bulk_data(guild.id, data_list[channel])

        await ctx.followup.send("Harvested data from the guild.")
        log.info(f"Harvested data from guild {guild.id} in {time.time() - start_time} seconds.")

    @commands.slash_command(name="get_all_messages")
    async def get_all_messages(self, ctx):
        self.manager.get_all_user_messages(ctx.guild.id, ctx.author.id)


# The `setup` function is required for the cog to work
# Don't change anything in this function, except for the

def setup(client):
    client.add_cog(Commands(client))
