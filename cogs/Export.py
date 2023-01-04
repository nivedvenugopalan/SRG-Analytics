import io

import discord
from discord.ext import commands
import chat_exporter


class Export(commands.Cog):
    def __init__(self, client):
        self.client = client

    export = discord.SlashCommandGroup("export", "Export data from the bot.")

    @export.command()
    async def html(self, ctx, channel: discord.TextChannel, limit: int = None):
        await ctx.defer()
        if limit is None:
            res = await chat_exporter.export(channel, bot=self.client)
        else:
            res = await chat_exporter.export(channel, limit=limit, bot=self.client)

        # send as virtual file
        transcript_file = discord.File(io.BytesIO(res.encode()),
                                       filename=f"{channel.id}.html")

        # todo: remove comment at the start of the file

        await ctx.followup.send(file=transcript_file)


def setup(client):
    client.add_cog(Export(client))
