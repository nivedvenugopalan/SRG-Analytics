import time

import discord
from discord.ext import commands
from backend import log, DataManager, error_template, embed_template


class Admin(commands.Cog):
    """Commands for guild admins"""

    def __init__(self, client):
        self.client = client

    admin = discord.SlashCommandGroup(name="admin", description="Commands for guild admins")

    ignore = admin.create_subgroup(name="ignore", description="Ignore a user from using the bot")
    unignore = admin.create_subgroup(name="unignore", description="Unignore a user from using the bot")

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Cog: Admin.py Loaded")

    @ignore.command(name="channel")
    @commands.has_permissions(administrator=True)
    async def ignore_channel(self, ctx, channel: discord.TextChannel | discord.threads.Thread = None):
        """Ignore a channel from the bot"""
        manager = DataManager()

        if channel is None:
            channel = ctx.channel

        # check if the channel is already ignored
        if manager.is_ignored(channel.id):
            await ctx.respond(embed=error_template("The given channel is already ignored"))
            return
        # check the type of the channel
        log.debug(f"Channel type: {type(channel)}")
        if type(channel) != discord.ChannelType.text or type(channel) != discord.threads.Thread:
            await ctx.respond(embed=error_template("The given channel is not a text channel"))
            return

        manager.set_ignores(channel.id, "channel", ctx.guild.id)

        embed = embed_template()
        embed.title = "Channel Ignored"
        embed.description = f"The channel {channel.mention} has been ignored"
        await ctx.respond(embed=embed)

    @unignore.command()
    @commands.has_permissions(administrator=True)
    async def unignore_channel(self, ctx, channel: discord.TextChannel | discord.threads.Thread = None):
        """Unignore a channel from the bot"""

        manager = DataManager()

        if channel is None:
            channel = ctx.channel

        # check if the channel is already ignored
        if not manager.is_ignored(channel.id):
            await ctx.respond(embed=error_template("The given channel is not ignored"))
            return

        manager.remove_ignores(channel.id)

        embed = embed_template()
        embed.title = "Channel Unignored"
        embed.description = f"The channel {channel.mention} has been unignored"
        await ctx.respond(embed=embed)

    @ignore.command()
    @commands.has_permissions(administrator=True)
    async def ignore_user(self, ctx, user: discord.User):
        """Ignore a user from the bot"""
        await ctx.send("Not implemented yet")

    @unignore.command()
    @commands.has_permissions(administrator=True)
    async def unignore_user(self, ctx, user: discord.User):
        """Unignore a user from the bot"""
        await ctx.send("Not implemented yet")

    @ignore.command()
    @commands.has_permissions(administrator=True)
    async def ignore_role(self, ctx, role: discord.Role):
        """Ignore a role from the bot"""
        await ctx.send("Not implemented yet")

    @unignore.command()
    @commands.has_permissions(administrator=True)
    async def unignore_role(self, ctx, role: discord.Role):
        """Unignore a role from the bot"""
        await ctx.send("Not implemented yet")

    @admin.command(name="harvest")
    @commands.has_permissions(administrator=True)
    async def harvest(self, ctx):
        await ctx.defer()
        manager = DataManager()

        guild = ctx.guild
        data_list = {}
        start_time = time.time()

        cmd_channel = self.client.get_channel(ctx.channel.id)

        async def harvest_channel(channel):
            # Iterate through all messages in the channel
            async for message in channel.history(limit=None):
                if message.author.bot:
                    continue

                if manager.is_ignored(ctx.channel.id):
                    return
                elif manager.is_ignored(ctx.author.id):
                    return
                # for role in ctx.author.roles:
                #     if self.manager.is_ignored(role.id):
                #         return
                # disabled cause will slow down the bot

                data_list[channel.name].append([
                    message.id, message.content, message.author.id, message.channel.id,
                    int(message.created_at.timestamp()) +
                    3 * 60 * 60, len(message.attachments),
                    message.reference.message_id if message.reference
                    else None, str([mention.id for mention in message.mentions]) if message.mentions != [] else None
                ])

        # Iterate through all channels in the guild
        for channel in guild.channels:

            # check if channel is a text channel
            if not isinstance(channel, discord.TextChannel):
                continue

            # Iterate through all messages in the channel
            data_list[channel.name] = []
            log.info(f"Harvesting channel {channel.name}...")
            try:
                await cmd_channel.send(f"Harvesting channel {channel.name}...")
            except Exception as err:
                log.error(err)

            await harvest_channel(channel)

        # Add the data to the database
        for channel in data_list:
            manager.add_bulk_data(guild.id, data_list[channel])

        await ctx.followup.send("Harvested data from the guild.")
        log.info(
            f"Harvested data from guild {guild.id} in {time.time() - start_time} seconds.")

    @admin.command(name="purge")
    @commands.has_permissions(administrator=True)
    async def purge(self, ctx):
        """Purge all data from the guild"""
        await ctx.defer()
        manager = DataManager()
        manager.purge_guild(ctx.guild.id)
        await ctx.followup.send("Purged data from the guild.")

    @admin.command(name="pause")
    @commands.has_permissions(administrator=True)
    async def pause(self, ctx):
        """Pause the bot from responding to commands"""
        manager = DataManager()

        if manager.is_paused(ctx.guild.id):
            await ctx.respond(embed=error_template("The bot is already paused"))
            return

        manager.pause(ctx.guild.id)
        embed = embed_template()
        embed.title = "Bot Paused"
        embed.description = "The bot has been paused"
        await ctx.respond(embed=embed)

    @admin.command(name="resume")
    @commands.has_permissions(administrator=True)
    async def unpause(self, ctx):
        """Unpause the bot from responding to commands"""
        manager = DataManager()

        if not manager.is_paused(ctx.guild.id):
            await ctx.respond(embed=error_template("The bot is not paused"))
            return

        manager.resume(ctx.guild.id)
        embed = embed_template()
        embed.title = "Bot resumed"
        embed.description = "The bot has been resumed"
        await ctx.respond(embed=embed)



def setup(client):
    client.add_cog(Admin(client))
