import disnake
from disnake.ext import commands
from core.any import CogExtension
import disnake.ext.commands.errors as err


class ErrorHandle(CogExtension):
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, "on_error"):    # 若該指令有自己的錯誤處理則不執行預設錯誤處理
            return
        if isinstance(error, err.MissingRequiredArgument):
            await ctx.send("缺少參數,可以用help確認用法")
        elif isinstance(error, err.CommandNotFound):
            await ctx.send("沒有這條指令,可以用help確認是否打錯字")
        elif isinstance(error, err.MissingPermissions):
            await ctx.send("沒有權限使用這條指令")
        else:
            await ctx.send("```diff\n-" + str(error) + "```")

    # @CMD_CLASS.CMD_NAME.error
    # async def cmd_error(self, ctx, error):


def setup(bot):
    bot.add_cog(ErrorHandle(bot))
