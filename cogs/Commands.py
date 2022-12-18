import time
import discord.ext.commands
from backend import *


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

    @commands.slash_command(name="profile", description="Shows your profile.")
    async def profile(self, ctx, user: discord.Member = None):
        await ctx.defer()
        if user is None:
            user = ctx.author

        if not ctx.guild:
            await ctx.followup.send("This command can only be used in a server.")
            return

        profile = self.manager.build_profile(ctx.guild.id, user.id)

        print("\n\n\n")
        print(profile)

        embed = discord.Embed(title=f"{user.name}'s Profile", color=discord.Color.blurple())
        embed.add_field(name="Guild ID", value=f"{ctx.guild.id}", inline=True)
        embed.add_field(name="User ID", value=f"{user.id}", inline=True)
        embed.add_field(name="Messages", value=f"{profile.no_of_messages}", inline=False)
        embed.add_field(name="Top 2 Words", value=f"{'`' + '`, `'.join([*[w[0] for w in profile.top_2_words], ]) + '`'}", inline=True)
        embed.add_field(name="Total Mentions", value=f"{profile.total_mentions}", inline=False)
        embed.add_field(name="Most Mentioned User", value=f"<@{profile.most_mentioned_person_id}>", inline=True)
        embed.add_field(name="Times Mentioned", value=f"{profile.total_times_mentioned}", inline=True)
        embed.add_field(name="Most Mentioned by", value=f"<@{profile.most_mentioned_by_id}>", inline=False)
        embed.add_field(name="Times", value=f"{profile.most_mentioned_by_id_no}", inline=True)

        await ctx.followup.send(embed=embed)

    @commands.slash_command(name="topten", description="Shows the top ten users in the guild.")
    async def topten(self, ctx):
        await ctx.defer()

        if not ctx.guild:
            await ctx.followup.send("This command can only be used in a server.")
            return

        # select the top 10 author_id s from the database based on how many times the author_id appears in the database
        self.manager.cur.execute(f"SELECT author_id, COUNT(author_id) FROM `{ctx.guild.id}` "
                                 f"GROUP BY author_id ORDER BY COUNT(author_id) DESC LIMIT 10")

        # fetch the data
        data = self.manager.cur.fetchall()

        # create an embed
        embed = discord.Embed(title=f"Top 10 Users in {ctx.guild.name}", color=0x00ff00)

        # iterate through the data
        for i in range(len(data)):
            # add a field to the embed
            embed.add_field(name=f"{i + 1}. {data[i][1]}",
                            value=f"<@{data[i][0]}>", inline=False)

        await ctx.followup.send(embed=embed)

    @commands.slash_command(name="topword", description="Shows the top word used in the guild.")
    async def topword(self, ctx):
        pass


# The `setup` function is required for the cog to work
# Don't change anything in this function, except for the

def setup(client):
    client.add_cog(Commands(client))
