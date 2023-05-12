import disnake
from disnake.ext import commands
from core.any import CogExtension
import json

with open("json/item.json", 'r', encoding="utf8") as file:
    data = json.load(file)


class Image(CogExtension):
    @commands.command()
    async def a(self, ctx):
        await ctx.send(file=disnake.File(data["A"]))


def setup(bot):
    bot.add_cog(Image(bot))
