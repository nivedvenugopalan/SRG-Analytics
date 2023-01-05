import io

import discord
import mplcyberpunk
from discord.ext import commands
from backend import log, DataManager, embed_template
from wordcloud import WordCloud as wc
import matplotlib.pyplot as plt


class WordCloud(commands.Cog):
    def __init__(self, client):
        self.client = client

    wordcloud = discord.SlashCommandGroup(name="wordcloud", description="WordCloud Commands")

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Cog: WordCloud.py Loaded")
        plt.style.use("cyberpunk")

    @wordcloud.command()
    async def wordcloud_user(self, ctx):
        messages = [("hello", 10), ("world", 15), ("goodbye", 5)]
        word_to_count = dict(messages)

        wordcloud = wc().generate_from_frequencies(word_to_count)

        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")

        mplcyberpunk.add_glow_effects()

        # save the graph as a virtual file and send it
        with io.BytesIO() as image_binary:
            plt.savefig(image_binary, format='png')
            image_binary.seek(0)

            embed = embed_template()
            embed.title = "Word Cloud"
            embed.description = "Shows the Word Cloud for a user."
            embed.set_image(url="attachment://image.png")

            await ctx.followup.send(embed=embed, file=discord.File(fp=image_binary, filename="image.png"))


def setup(client):
    client.add_cog(WordCloud(client))
