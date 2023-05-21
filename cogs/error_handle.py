import disnake
from disnake.ext import commands
from core.any import CogExtension
import disnake.ext.commands.errors as err
import traceback
import json
from datetime import datetime
import os

with open("json/setting.json", "r") as f:
    debug = json.load(f)["debug"]


class ErrorHandle(CogExtension):
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        debug_ch = self.bot.get_guild(int(debug["debug_guild"])).get_channel(int(debug["debug_channel"]))
        if hasattr(ctx.command, "on_error"):    # 若該指令有自己的錯誤處理則不執行預設錯誤處理
            return
        if isinstance(error, err.MissingRequiredArgument):
            await ctx.send("缺少參數,可以用help確認用法")
        elif isinstance(error, err.CommandNotFound):
            await ctx.send("沒有這條指令,可以用help確認是否打錯字")
        elif isinstance(error, err.MissingPermissions):
            await ctx.send("沒有權限使用這條指令")
        else:
            err_msg = "".join(traceback.format_exception(error))
            await debug_ch.send("```ps\n[\nAn error occurred in command " + ctx.command.name + "\n" + err_msg + "]```")

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter, error):
        debug_ch = self.bot.get_guild(int(debug["debug_guild"])).get_channel(int(debug["debug_channel"]))
        if hasattr(inter.application_command, "on_error"):  # 若該指令有自己的錯誤處理則不執行預設錯誤處理
            return
        if isinstance(error, err.CommandOnCooldown):
            pass
        elif isinstance(error, err.BadArgument):
            await inter.response.send_message("輸入參數有誤")
        else:
            err_msg = "".join(traceback.format_exception(error))
            if len(err_msg) > 1900:
                err_file_name = f"error_{datetime.strftime(datetime.now(), '%Y_%m_%d_%H_%M_%S')}.txt"
                with open(err_file_name, "w", encoding="UTF-8") as err_file:
                    err_file.write(err_msg)
                with open(err_file_name, "rb") as err_file:
                    await debug_ch.send(file=disnake.File(err_file))
                os.remove(f"./{err_file_name}")
            else:
                await debug_ch.send(
                    "```ps\n[\nAn error occurred in command " + inter.application_command.name + "\n" + err_msg + "]```"
                )
    # @CMD_CLASS.CMD_NAME.error
    # async def cmd_error(self, ctx/inter, error):


def setup(bot):
    bot.add_cog(ErrorHandle(bot))
