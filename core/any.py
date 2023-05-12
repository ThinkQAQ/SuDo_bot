import disnake
from disnake.ext import commands


# 這邊可以使用Cog功能繼承基本屬性
class CogExtension(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
