import io
import random

import discord.ext.commands
import pytz as pytz
import matplotlib.pyplot as plt
from backend import *


class Commands(commands.Cog):
    def __init__(self, client):
        self.client = client
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
        log.info(
            f"Harvested data from guild {guild.id} in {time.time() - start_time} seconds.")

    @commands.slash_command(name="profile", description="Shows your profile.")
    async def profile(self, ctx, user: discord.Member = None):
        await ctx.defer()
        self.manager = DataManager()
        if user is None:
            user = ctx.author

        if not ctx.guild:
            await ctx.followup.send("This command can only be used in a server.")
            return

        profile = self.manager.build_profile(ctx.guild.id, user.id)

        embed = discord.Embed(
            title=f"{user.name}'s Profile", color=discord.Color.blurple())
        embed.add_field(name="Guild ID", value=f"{ctx.guild.id}", inline=True)
        embed.add_field(name="User ID", value=f"{user.id}", inline=True)
        embed.add_field(name="Messages",
                        value=f"{profile.no_of_messages}", inline=False)
        embed.add_field(name="Top 5 Words", value=", ".join(
            [f"`{w[0]}`" for w in profile.top_2_words]), inline=True)
        embed.add_field(name="Total Mentions",
                        value=f"{profile.total_mentions}", inline=False)
        embed.add_field(name="Most Mentioned User",
                        value=f"<@{profile.most_mentioned_person_id}>", inline=True)
        embed.add_field(name="Times Mentioned",
                        value=f"{profile.total_times_mentioned}", inline=True)
        embed.add_field(name="Most Mentioned by",
                        value=f"<@{profile.most_mentioned_by_id}>", inline=True)
        embed.add_field(
            name="Times", value=f"{profile.most_mentioned_by_id_no}", inline=True)
        embed.add_field(name="Most Active Channel",
                        value=f"<#{profile.active_channel}>", inline=True)

        await ctx.followup.send(embed=embed)

    @commands.slash_command(name="topten", description="Shows the top ten users in the guild.")
    async def topten(self, ctx):
        await ctx.defer()
        self.manager = DataManager()

        if not ctx.guild:
            await ctx.followup.send("This command can only be used in a server.")
            return

        # select the top 10 author_id s from the database based on how many times the author_id appears in the database
        self.manager.cur.execute(f"SELECT author_id, COUNT(author_id) FROM `{ctx.guild.id}` "
                                 f"GROUP BY author_id ORDER BY COUNT(author_id) DESC LIMIT 10")

        # fetch the data
        data = self.manager.cur.fetchall()

        # create an embed
        embed = discord.Embed(
            title=f"Top 10 Users in {ctx.guild.name}", color=0x00ff00)

        # iterate through the data
        for i in range(len(data)):
            # add a field to the embed
            embed.add_field(name=f"{i + 1}. {data[i][1]}",
                            value=f"<@{data[i][0]}>", inline=False)

        await ctx.followup.send(embed=embed)

    @commands.slash_command(name="topchannel", description="Shows the help menu.")
    async def topchannel(self, ctx):
        self.manager = DataManager()
        self.manager.cur.execute(
            f"SELECT channel_id, COUNT(channel_id) FROM `{ctx.guild.id}` LIMIT 5 ORDER BY COUNT(channel_id) DESC")
        data = self.manager.cur.fetchall()
        embed = discord.Embed(
            title=f"Top 5 Channels in {ctx.guild.name}", color=0x00ff00)
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

    @commands.slash_command(name="member_activeness",
                            description="Shows the times where a member was active in a guild.")
    async def member_activeness(self, ctx, user_1: discord.User, user_2: discord.User = None,
                                user_3: discord.User = None,
                                user_4: discord.User = None):
        await ctx.defer()
        manager = DataManager()
        epochs = []

        for user in [user_1, user_2, user_3, user_4]:
            if user is None:
                continue
            manager.cur.execute(
                f"SELECT epoch FROM `{ctx.guild.id}` WHERE `author_id` = ?", (user.id,))
            epochs.append(list(manager.cur.fetchall()))

        epochs = [epoch for epoch in epochs if epoch != []]
        tz = pytz.timezone('Asia/Riyadh')

        fig, axs = plt.subplots(1, 1)
        data = []

        # iterate over the list of epochs
        for epoch_list in epochs:
            # create a dictionary to store the counts for each hour
            hour_counts = {i: 0 for i in range(24)}
            # iterate over the epochs in each sublist
            for epoch in epoch_list:
                # convert the epoch to a datetime object
                dt = datetime.datetime.fromtimestamp(epoch[0], tz=tz)
                # extract the hour from the datetime object
                hour = dt.hour
                # increment the count for this hour in the dictionary
                if hour in hour_counts:
                    hour_counts[hour] += 1
                else:
                    hour_counts[hour] = 1
            # extract the hours and counts as separate lists
            hours = list(hour_counts.keys())
            counts = list(hour_counts.values())
            # store the data for this sublist
            data.append((hours, counts))

        sublist_names = [f"{user.name}" for user in [
            user_1, user_2, user_3, user_4] if user is not None]

        t = [i for i in range(24)]

        # plot the data
        for i, (hours, counts) in enumerate(data):
            axs.plot(t, counts, '-o', label=sublist_names[i])

        ticks = [i for i in range(24)]
        tick_labels = [str(i) for i in range(24)]

        # set the tick locations and labels
        axs.set_xticks(ticks)
        axs.set_xticklabels(tick_labels)

        # add labels and grid
        axs.set_xlabel('Hour')
        axs.set_ylabel('Number of Occurrences')
        axs.grid(True)

        # add a title
        axs.set_title('Number of Occurrences by Hour')

        # show a legend
        axs.legend()

        # adjust the layout
        fig.tight_layout()

        # save the graph as a virtual file and send it
        with io.BytesIO() as image_binary:
            fig.savefig(image_binary, format='png')
            image_binary.seek(0)
            embed = discord.Embed(
                title="Member activeness per hour", color=0x00ff00)
            embed.set_image(url="attachment://image.png")
            await ctx.followup.send(embed=embed, file=discord.File(fp=image_binary, filename="image.png"))

        # close the figure
        plt.close(fig)

    @commands.slash_command(name="server_activeness", description="")
    async def server_activeness(self, ctx):
        await ctx.defer()
        manager = DataManager()
        epochs = []

        manager.cur.execute(f"SELECT epoch FROM `{ctx.guild.id}`", )
        epochs.append(list(manager.cur.fetchall()))
        epochs = epochs[0]

        tz = pytz.timezone('Asia/Riyadh')

        fig, axs = plt.subplots(1, 1)

        epochs = [list(epoch)[0] for epoch in epochs if epoch != []]

        # iterate over the list of epochs
        month_counts = {i: 0 for i in range(1, 13)}
        # iterate over the epochs in each sublist
        for epoch in epochs:
            # convert the epoch to a datetime object
            dt = datetime.datetime.fromtimestamp(epoch, tz=tz)
            # extract the month from the datetime object
            month = dt.month
            # increment the count for this month in the dictionary
            if month in month_counts:
                month_counts[month] += 1
            else:
                month_counts[month] = 1
        # extract the months and counts as separate lists
        counts = list(month_counts.values())

        t = [i for i in range(len(counts))]

        # plot the data
        axs.plot(t, counts, '-o')

        ticks = [i for i in range(12)]
        tick_labels = [datetime.datetime(
            2022, i, 1).strftime('%b') for i in range(1, 13)]

        # set the tick locations and labels
        axs.set_xticks(ticks)
        axs.set_xticklabels(tick_labels)

        # add labels and grid
        axs.set_xlabel('Month')
        axs.set_ylabel('Number of Occurrences')
        axs.grid(True)

        # add a title
        axs.set_title('Number of Occurrences by Month')

        # adjust the layout
        fig.tight_layout()

        # save the graph as a virtual file and send it
        with io.BytesIO() as image_binary:
            fig.savefig(image_binary, format='png')
            image_binary.seek(0)
            embed = discord.Embed(
                title="Server activeness per month", color=discord.Color.blue())
            embed.set_image(url="attachment://image.png")
            await ctx.followup.send(embed=embed, file=discord.File(fp=image_binary, filename="image.png"))

        # close the figure
        plt.close(fig)

    @commands.slash_command(name="member_activeness_per_month",
                            description="Shows the months where a member was active in a guild.")
    async def member_activeness_per_month(self, ctx, user_1: discord.User, user_2: discord.User = None,
                                          user_3: discord.User = None,
                                          user_4: discord.User = None):
        await ctx.defer()
        manager = DataManager()
        epochs = []

        for user in [user_1, user_2, user_3, user_4]:
            if user is None:
                continue
            manager.cur.execute(
                f"SELECT epoch FROM `{ctx.guild.id}` WHERE `author_id` = ?", (user.id,))
            epochs.append(list(manager.cur.fetchall()))

        epochs = [epoch for epoch in epochs if epoch != []]
        tz = pytz.timezone('Asia/Riyadh')

        fig, axs = plt.subplots(1, 1)
        data = []

        # iterate over the list of epochs
        for epoch_list in epochs:
            # create a dictionary to store the counts for each month
            month_counts = {i: 0 for i in range(1, 13)}
            # iterate over the epochs in each sublist
            for epoch in epoch_list:
                # convert the epoch to a datetime object
                dt = datetime.datetime.fromtimestamp(epoch[0], tz=tz)
                # extract the month from the datetime object
                month = dt.month
                # increment the count for this month in the dictionary
                if month in month_counts:
                    month_counts[month] += 1
                else:
                    month_counts[month] = 1
            # extract the months and counts as separate lists
            months = list(month_counts.keys())
            counts = list(month_counts.values())
            # store the data for this sublist
            data.append((months, counts))

        sublist_names = [f"{user.name}" for user in [
            user_1, user_2, user_3, user_4] if user is not None]

        t = [i for i in range(1, 13)]

        # plot the data
        for i, (months, counts) in enumerate(data):
            axs.plot(t, counts, '-o', label=sublist_names[i])

        ticks = [i for i in range(1, 13)]
        tick_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May',
                       'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        # set the tick locations and labels
        axs.set_xticks(ticks)
        axs.set_xticklabels(tick_labels)

        # add labels and grid
        axs.set_xlabel('Month')
        axs.set_ylabel('Number of Occurrences')
        axs.grid(True)

        # add a title
        axs.set_title('Member Activeness per Month')

        # show a legend
        axs.legend()

        # adjust the layout
        fig.tight_layout()

        # save the graph as a virtual file and send it
        with io.BytesIO() as image_binary:
            fig.savefig(image_binary, format='png')
            image_binary.seek(0)
            embed = discord.Embed(
                title="Number of Occurrences by Month", color=discord.Color.blue())
            embed.set_image(url="attachment://image.png")
            await ctx.followup.send(embed=embed, file=discord.File(fp=image_binary, filename="image.png"))

        # close the figure
        plt.close(fig)


# The `setup` function is required for the cog to work
# Don't change anything in this function, except for the

def setup(client):
    client.add_cog(Commands(client))
