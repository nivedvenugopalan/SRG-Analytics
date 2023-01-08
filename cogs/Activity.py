import time

import discord
from discord.ext import commands
import pytz
import datetime
import io
import matplotlib.pyplot as plt
import mplcyberpunk
from backend import log, DataManager, embed_template


class Activity(commands.Cog):
    def __init__(self, client):
        self.client = client

    activity = discord.SlashCommandGroup("activity", "Activity commands")

    user_activity = activity.create_subgroup(
        "user", "Monthly activity commands")
    server_activity = activity.create_subgroup(
        "server", "Daily activity commands")

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Cog: Activity.py Loaded")
        plt.style.use("cyberpunk")

    @user_activity.command(
        name="hourly",
        description="Shows the activity of a user in a guild on a per hour basis."
    )
    async def member_hourly_activeness(
            self, ctx,
            user_1: discord.Member,
            user_2: discord.Member = None,
            user_3: discord.Member = None,
            user_4: discord.Member = None,
            user_5: discord.Member = None,
            average: bool = False
    ):
        await ctx.defer()
        manager = DataManager()
        epochs = []

        users = [x for x in [user_1, user_2, user_3,
                             user_4, user_5] if x is not None]
        for user in users:
            manager.cur.execute(
                f"SELECT epoch FROM `{ctx.guild.id}` WHERE `author_id` = ?", (user.id,))
            epochs.append(list(manager.cur.fetchall()))

        epochs = [epoch for epoch in epochs if epoch != []]
        tz = pytz.timezone('Asia/Riyadh')

        fig, axs = plt.subplots(1, 1)
        data = []

        epochs = [sorted(epoch_list, key=lambda x: x[0])
                  for epoch_list in epochs]

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

        if average is True:
            for i in range(len(users)):
                first_msg_time = datetime.datetime.fromtimestamp(
                    epochs[i][0][0])
                current_time = datetime.datetime.now()
                interval_days = (current_time - first_msg_time).days

                if interval_days == 0:
                    interval_days = 1

                data[i] = (
                    data[i][0], [x / interval_days for x in list(data[i][1])])

        sublist_names = [f"{user.display_name}" for user in [
            user_1, user_2, user_3, user_4, user_5] if user is not None]

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
        axs.set_ylabel(
            'Number of Messages' if average is False else 'Average Number of Messages')
        axs.grid(True)

        # add a title
        axs.set_title(
            'Hourly Member Activity' if average is False else 'Average Hourly Member Activity')
        axs.legend()
        fig.tight_layout()

        mplcyberpunk.add_glow_effects()

        # save the graph as a virtual file and send it
        with io.BytesIO() as image_binary:
            fig.savefig(image_binary, format='png')
            image_binary.seek(0)

            embed = embed_template()
            embed.title = "Hourly Member Activity"
            embed.description = "Shows the activity of user(s) in a guild on a per hour basis."
            embed.set_image(url="attachment://image.png")

            await ctx.followup.send(embed=embed, file=discord.File(fp=image_binary, filename="image.png"))

        # close the figure
        plt.close(fig)

    @user_activity.command(
        name="monthly",
        description="Shows the activity of a user in a guild on a monthly basis."
    )
    async def member_monthly_activeness(
            self, ctx,
            user_1: discord.Member,
            user_2: discord.Member = None,
            user_3: discord.Member = None,
            user_4: discord.Member = None,
            user_5: discord.Member = None,
            average: bool = False
    ):
        await ctx.defer()
        manager = DataManager()
        epochs = []

        users = [x for x in [user_1, user_2, user_3,
                             user_4, user_5] if x is not None]
        for user in users:
            manager.cur.execute(
                f"SELECT epoch FROM `{ctx.guild.id}` WHERE `author_id` = ?", (user.id,))
            epochs.append(list(manager.cur.fetchall()))

        epochs = [epoch for epoch in epochs if epoch != []]
        tz = pytz.timezone('Asia/Riyadh')

        fig, axs = plt.subplots(1, 1)
        data = []

        epochs = [sorted(epoch_list, key=lambda x: x[0])
                  for epoch_list in epochs]

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

        if average is True:
            for i in range(len(users)):
                first_msg_time = datetime.datetime.fromtimestamp(
                    epochs[i][0][0])
                current_time = datetime.datetime.now()
                interval_months = (
                                          current_time - first_msg_time).days / 30.436875

                if interval_days == 0:
                    interval_days = 1

                data[i] = (
                    data[i][0], [x / interval_months for x in list(data[i][1])])

        sublist_names = [f"{user.display_name}" for user in [
            user_1, user_2, user_3, user_4, user_5] if user is not None]

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
        axs.set_ylabel(
            'Number of Messages' if average is False else 'Average Number of Messages')
        axs.grid(True)

        # add a title
        axs.set_title(
            'Monthly Member Activity' if average is False else 'Average Monthly Member Activity')
        axs.legend()
        fig.tight_layout()

        mplcyberpunk.add_glow_effects()

        # save the graph as a virtual file and send it
        with io.BytesIO() as image_binary:
            fig.savefig(image_binary, format='png')
            image_binary.seek(0)

            embed = embed_template()
            embed.title = "Monthly Member Activity"
            embed.description = "Shows the activity of user(s) in a guild on a per month basis."

            embed.set_image(url="attachment://image.png")
            await ctx.followup.send(embed=embed, file=discord.File(fp=image_binary, filename="image.png"))

        # close the figure
        plt.close(fig)

    @server_activity.command(
        name="monthly",
        description="Shows the activity of a guild on a per month basis."
    )
    async def server_monthly_activeness(self, ctx):
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
        axs.set_ylabel('Number of Messages')
        axs.grid(True)

        axs.set_title('Monthly Server Activity')
        fig.tight_layout()

        mplcyberpunk.add_glow_effects()

        # save the graph as a virtual file and send it
        with io.BytesIO() as image_binary:
            fig.savefig(image_binary, format='png')
            image_binary.seek(0)
            embed = embed_template()
            embed.title = "Monthly Server Activity"
            embed.description = "Shows the activity of a guild on a per month basis."
            embed.set_image(url="attachment://image.png")
            await ctx.followup.send(embed=embed, file=discord.File(fp=image_binary, filename="image.png"))

        # close the figure
        plt.close(fig)

    @server_activity.command(
        name="hourly",
        description="Shows the activity of a guild on a per hour basis."
    )
    async def server_hourly_activeness(self, ctx):
        pass  # TODO

    @server_activity.command(
        name="today",
        description="Shows the activity of a guild today."
    )
    async def server_today_activeness(self, ctx):
        await ctx.defer()
        manager = DataManager()
        epochs = []

        # SELECT EPOCH OF TODAY
        manager.cur.execute(f"SELECT epoch FROM `{ctx.guild.id}` WHERE epoch > {int(time.time()) - 86400}")
        epochs.append(list(manager.cur.fetchall()))
        epochs = epochs[0]

        tz = pytz.timezone('Asia/Riyadh')

        fig, axs = plt.subplots(1, 1)

        epochs = [list(epoch)[0] for epoch in epochs if epoch != []]

        # iterate over the list of epochs
        hour_counts = {i: 0 for i in range(0, 24)}
        # iterate over the epochs in each sublist
        for epoch in epochs:
            # convert the epoch to a datetime object
            dt = datetime.datetime.fromtimestamp(epoch, tz=tz)
            # extract the month from the datetime object
            hour = dt.hour
            # increment the count for this month in the dictionary
            if hour in hour_counts:
                hour_counts[hour] += 1
            else:
                hour_counts[hour] = 1
        # extract the months and counts as separate lists
        counts = list(hour_counts.values())

        t = [i for i in range(len(counts))]

        # plot the data
        axs.plot(t, counts, '-o')

        ticks = [i for i in range(24)]
        tick_labels = [i for i in range(24)]

        # set the tick locations and labels
        axs.set_xticks(ticks)
        axs.set_xticklabels(tick_labels)

        # add labels and grid
        axs.set_xlabel('Hour')
        axs.set_ylabel('Number of Messages')
        axs.grid(True)

        axs.set_title("Today's Server Activity")
        fig.tight_layout()

        mplcyberpunk.add_glow_effects()

        # save the graph as a virtual file and send it
        with io.BytesIO() as image_binary:
            fig.savefig(image_binary, format='png')
            image_binary.seek(0)
            embed = embed_template()
            embed.title = "Today's Server Activity"
            embed.description = "Shows the activity of a guild today."
            embed.set_image(url="attachment://image.png")
            await ctx.followup.send(embed=embed, file=discord.File(fp=image_binary, filename="image.png"))

        # close the figure
        plt.close(fig)



def setup(client):
    client.add_cog(Activity(client))
