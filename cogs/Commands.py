import time
from discord.ext import commands
import discord
from backend import DataManager, log, Profile, embed_template


class Commands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.count = 0

    # Use @command.Cog.listener() for an event-listener (on_message, on_ready, etc.)
    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Cog: Commands.py Loaded")

    @commands.slash_command(name="harvest", description="Harvests data from a guild.")
    async def harvest(self, ctx):
        await ctx.defer()
        self.manager = DataManager()

        guild = ctx.guild
        data_list = {}
        start_time = time.time()

        cmd_channel = self.client.get_channel(ctx.channel.id)

        async def harvest_channel(channel):
            # Iterate through all messages in the channel
            async for message in channel.history(limit=None):
                if message.author.bot:
                    continue

                data_list[channel.name].append([
                    message.id, message.content, message.author.id, message.channel.id,
                    int(message.created_at.timestamp()) +
                    3 * 60 * 60, len(message.attachments),
                    message.reference.message_id if message.reference
                    else None, str([mention.id for mention in message.mentions]) if message.mentions != [] else None
                ])
                self.count += 1
                if self.count % 1000 == 0:
                    print(self.count)

        # Iterate through all channels in the guild
        for channel in guild.channels:

            # check if channel is a text channel
            if not isinstance(channel, discord.TextChannel):
                if isinstance(channel, discord.ForumChannel):
                    for thread in channel.threads:
                        data_list[thread.name] = []
                        await harvest_channel(thread)

            else:
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
            print(channel)
            self.manager.add_bulk_data(guild.id, data_list[channel])

        await ctx.followup.send("Harvested data from the guild.")
        log.info(
            f"Harvested data from guild {guild.id} in {time.time() - start_time} seconds.")

    @commands.slash_command(name="profile", description="Shows your profile.")
    async def profile(self, ctx, user: discord.Member = None):
        await ctx.defer()
        manager = DataManager()
        if user is None:
            user = ctx.author

        if not ctx.guild:
            await ctx.followup.send("This command can only be used in a server.")
            return

        profile = manager.build_profile(ctx.guild.id, user.id)

        embed = embed_template()
        embed.title = f"User Profile"
        embed.description = f"{user.mention}'s profile."

        embed.add_field(name="Guild ID", value=f"`{ctx.guild.id}`", inline=True)
        embed.add_field(name="User ID", value=f"`{user.id}`", inline=True)
        embed.add_field(name="Messages", value=f"`{profile.no_of_messages}`", inline=True)
        embed.add_field(name="Top Words", value=", ".join([f"`{w[0]}`" for w in profile.top_2_words]), inline=False)

        embed.add_field(name="Total Mentions", value=f"`{profile.total_mentions}`", inline=True)
        embed.add_field(name="Most Mentioned User", value=f"<@{profile.most_mentioned_person_id}>", inline=True)

        embed.add_field(name="Most Active Channel", value=f"<#{profile.active_channel}>", inline=False)

        embed.add_field(name="Times Mentioned", value=f"`{profile.total_times_mentioned}`", inline=True)
        embed.add_field(name="Most Mentioned by", value=f"<@{profile.most_mentioned_by_id}>", inline=True)
        embed.add_field(name="Times", value=f"{profile.most_mentioned_by_id_no}", inline=True)

        await ctx.followup.send(embed=embed)

    @commands.slash_command(name="topten", description="Shows the top ten users in the guild.")
    async def topten(self, ctx):
        await ctx.defer()
        manager = DataManager()

        if not ctx.guild:
            await ctx.followup.send("This command can only be used in a server.")
            return

        # select the top 10 author_id s from the database based on how many times the author_id appears in the database
        manager.cur.execute(f"SELECT author_id, COUNT(author_id) FROM `{ctx.guild.id}` "
                            "GROUP BY author_id ORDER BY COUNT(author_id) DESC LIMIT 10")

        # fetch the data
        data = manager.cur.fetchall()

        # create an embed
        embed = embed_template()
        embed.title = "Top 10 Users"
        embed.description = "The top 10 users in this guild, by messages."

        # iterate through the data
        for i in range(len(data)):
            # add a field to the embed
            embed.add_field(name=f"{i + 1}. {data[i][1]}",
                            value=f"<@{data[i][0]}>", inline=False)

        await ctx.followup.send(embed=embed)

    @commands.slash_command(name="topchannel", description="Shows the help menu.")
    async def topchannel(self, ctx):
        manager = DataManager()
        manager.cur.execute(
            f"SELECT channel_id, COUNT(channel_id) FROM `{ctx.guild.id}` LIMIT 5 ORDER BY COUNT(channel_id) DESC")
        data = manager.cur.fetchall()
        embed = embed_template()
        embed.title = "Top 5 Channels"
        embed.description = "The top 5 channels in this guild, by messages."
        for i in range(len(data)):
            embed.add_field(name=f"{i + 1}. {data[i][1]}",
                            value=f"<#{data[i][0]}>", inline=False)
        await ctx.followup.send(embed=embed)

    @commands.slash_command(name="topwords", description="Shows the top word said by the user in a guild.")
    async def topwords(self, ctx):
        words = Profile.most_user_words(ctx.author.id, ctx.guild.id, n=20)
        embed = discord.Embed(
            title=f"Top 20 words said by {ctx.author.name}", color=0x00ff00)

        for i, word in enumerate(words, start=1):
            embed.add_field(
                name=f"{i}. {word[0]}", value=f"({word[1]})", inline=False)

        await ctx.followup.send(embed=embed)


# The `setup` function is required for the cog to work
# Don't change anything in this function, except for the

def setup(client):
    client.add_cog(Commands(client))
