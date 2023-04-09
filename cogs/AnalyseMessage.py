import discord
from datetime import datetime
from discord.ext import commands
from backend import embed_template

from mat import sentiment_analysis, entity_recognition, pos_tagging, language, grammar_police


class AnalyseMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.message_command()
    async def analyse(self, ctx, message: discord.Message):

        # make an embed
        embed = embed_template()
        embed.title = f"Message Analysis"
        embed.description = f"Server: {ctx.guild.name}"

        embed.add_field(name="Message ID", value=f"`{message.id}`")
        embed.add_field(
            name="Author", value=f"<@{message.author.id}>")
        embed.add_field(
            name="Channel", value=f"<#{message.channel.id}>")
        embed.add_field(
            name="Content", value=f"`{message.content}`", inline=False)
        embed.add_field(
            name="Timestamp", value=f"`{message.created_at.strftime('%Y-%m-%d %H:%M:%S')}`")
        polarity, subjectivity = sentiment_analysis(message.content)

        embed.add_field(
            name="Polarity", value=f"`{polarity}`", inline=False)
        embed.add_field(
            name="Subjectivity", value=f"`{subjectivity}`", inline=False)

        embed.add_field(
            name="Entities", value=", ".join(
                [f"```{e[0]}```" for e in entity_recognition.get_entities(
                    message.content)]
            )
        )

        embed.add_field(
            name="Language", value=f"`{language.detect_language(message.content)}`", inline=False)
        # if language not en, translate it
        if language.detect_language(message.content) != "en":
            embed.add_field(
                name="Translated", value=f"`{language.translate(message.content)}`", inline=False)

        # grammar
        embed.add_field(
            name="Grammar", value=", ".join(
                [f"```{g}```" for g in grammar_police.get_grammar(
                    message.content)]
            )
        )

        image = pos_tagging.get_pos_tagged_img(message.content)
        embed.set_image(url="attachment://image.png")

        await ctx.reply(embed=embed, file=discord.File(image, filename="image.png"))


# The `setup` function is required for the cog to work
# Don't change anything in this function, except for the
def setup(client):
    client.add_cog(AnalyseMessage(client))
