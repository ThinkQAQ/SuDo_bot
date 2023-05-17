import disnake
from disnake.ext import commands
from core.any import CogExtension
import json

with open("json/item.json", 'r', encoding="utf8") as file:
    data = json.load(file)


class Image(CogExtension):
    @commands.slash_command(description="A", dm_permission=False)
    async def a(self, inter):
        await inter.response.send_message(file=disnake.File(data["A"]))


def setup(bot):
    bot.add_cog(Image(bot))
