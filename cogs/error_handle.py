import disnake
from disnake.ext import commands
from core.any import CogExtension
import disnake.ext.commands.errors as err
import traceback
import json
from datetime import datetime
import os

with open("json/setting.json", "r") as f:
    data = json.load(f)
    if "debug" in data:
        debug = data["debug"]
    else:
        debug = 0


class ErrorHandle(CogExtension):
    @staticmethod
    def store_channel_data():
        with open("json/setting.json", "w") as file:
            json.dump(data, file, indent=4)

    @commands.slash_command(description="設定debug頻道")
    @commands.is_owner()
    async def set_debug_ch(self, inter,
                           guild_id: int = commands.Param(name="伺服器id", large=True),
                           channel_id: int = commands.Param(name="頻道id", large=True)
                           ):
        guild = self.bot.get_guild(guild_id)

        if guild is None:
            await inter.response.send_message("找不到伺服器")
            return
        if guild.get_channel(channel_id) is None:
            await inter.response.send_message("找不到頻道")
            return

        data["debug"] = {"debug_guild": str(guild_id), "debug_channel": str(channel_id)}
        global debug
        debug = data["debug"]
        self.store_channel_data()
        await inter.response.send_message("設置成功")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if debug == 0:
            return
        debug_ch = self.bot.get_guild(int(debug["debug_guild"])).get_channel(int(debug["debug_channel"]))
        if hasattr(ctx.command, "on_error"):  # 若該指令有自己的錯誤處理則不執行預設錯誤處理
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
        if debug == 0:
            return
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
