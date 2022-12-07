import discord
from discord.ext import commands
from dataManagement import DataManager


class processMessages(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, ctx):
        print(ctx)
        print(str(ctx.content))
        x = DataManager()
        x.conn(ctx.guild.id)
        x.addData(ctx.id, ctx.content, ctx.author.id)
        print("Data Added")


def setup(client):
    client.add_cog(processMessages(client))
