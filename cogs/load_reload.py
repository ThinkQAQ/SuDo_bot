import disnake
from disnake.ext import commands
from core.any import CogExtension


class LoadReload(CogExtension):
    @commands.command()
    @commands.is_owner()  # owner only command
    async def load(self, ctx, extension):
        self.bot.load_extension(f"cogs.{extension}")
        await ctx.author.send(f"{extension} is load")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, extension):
        self.bot.unload_extension(f"cogs.{extension}")
        await ctx.author.send(f"{extension} is unload")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, extension):
        # 如果直接更改程式碼的話就直接reload
        self.bot.reload_extension(f"cogs.{extension}")
        await ctx.author.send(f"{extension} is reload")


def setup(bot):
    bot.add_cog(LoadReload(bot))
