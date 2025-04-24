import disnake
from disnake import Event, ui
from disnake.ext import commands, tasks
from core.any import CogExtension
import json
from datetime import datetime, timedelta, timezone
import time

qu = []
with open("json/reminder.json", "r") as f:
    data = json.load(f)
    while len(data) != 0:
        if int(data[0][1]) < int(time.time()):
            data.pop(0)
            continue
        qu.append(data.pop(0))


class Reminder(CogExtension):
    def __init__(self, bot):
        super().__init__(bot)

    @staticmethod
    def store_timer_data():
        with open("json/reminder.json", "w") as file:
            json.dump(qu, file, indent=4)

    @tasks.loop(seconds=1)
    async def time_check(self):
        if len(qu) == 0:
            self.time_check.cancel()
        for e in qu:
            if int(e[1]) <= int(time.time()):
                t = timezone(timedelta(hours=8))
                timestamp = datetime.now(t)

                embed = disnake.Embed(title="SuDo Reminder", color=0x9bff80)
                # embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                embed.add_field(name="時間到啦!", value=e[0], inline=True)
                embed.set_footer(text="\u200b")
                embed.timestamp = timestamp
                await self.bot.get_channel(e[2]).send(content="<@" + str(e[3]) + ">", embed=embed)
                qu.remove(e)
                self.store_timer_data()

    @commands.slash_command(description="設置提醒通知", dm_permission=False)
    async def set_reminder(self, inter, descrip: str = commands.Param(name="提醒事項"),
                           t_time: str = commands.Param(name="提醒時間", description="請以Unix時間戳表示")):
        if int(t_time) < int(time.time()):
            await inter.response.send_message("不能設置之前的時間")
            return

        element = [descrip, t_time, inter.channel.id, inter.user.id]
        qu.append(element)

        await inter.response.send_message("設置成功")
        self.store_timer_data()
        await self.time_check.start()

    @commands.slash_command(description="查詢已設置的提醒", dm_permission=False)
    async def list_reminder(self, inter):
        if len(qu) == 0:
            await inter.response.send_message("當前沒有已設置的提醒")
            return
        t = timezone(timedelta(hours=8))
        timestamp = datetime.now(t)
        embed = disnake.Embed(title="SuDo Reminder", color=0x9bff80)
        # embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        embed.add_field(name="共" + str(len(qu)) + "個提醒", value="", inline=True)
        for e in qu:
            embed.add_field(name="", value=e[0], inline=False)
        embed.set_footer(text="\u200b")
        embed.timestamp = timestamp
        await inter.response.send_message(content="<@" + str(e[3]) + ">", embed=embed)


def setup(bot):
    bot.add_cog(Reminder(bot))
