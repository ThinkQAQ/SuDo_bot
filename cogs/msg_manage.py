import disnake
from disnake.ext import commands, tasks
from core.any import CogExtension
from disnake import ui, Event, Embed
import json
from datetime import datetime, timedelta, timezone
from util.audit_var import AuditData
import atexit

with open("json/msg_manage_setting.json", "r") as f:
    data = json.load(f)


class YesNoButton(ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @ui.button(label="Yes", style=disnake.ButtonStyle.green, custom_id="y")
    async def yes_callback(self, button: ui.Button, interaction: disnake.Interaction):
        another_button = [x for x in self.children if x.custom_id == "n"][0]
        button.disabled = True
        another_button.disabled = True
        self.value = True
        await interaction.response.send_message("確認更改")

    @ui.button(label="No", style=disnake.ButtonStyle.red, custom_id="n")
    async def no_callback(self, button: ui.Button, interaction: disnake.Interaction):
        another_button = [x for x in self.children if x.custom_id == "y"][0]
        button.disabled = True
        another_button.disabled = True
        self.value = False
        await interaction.response.send_message("確認取消")


class MsgManage(CogExtension):
    def __init__(self, bot):
        super().__init__(bot)
        self.clean_audit_variable.start()
        self.bot_delete_edit = False  # whether is bot delete/edit message

    @staticmethod
    def store_channel_data():
        with open("json/msg_manage_setting.json", "w") as file:
            json.dump(data, file, indent=4)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        # if message.content == 'ping':
        #     await message.channel.send('pong')

        # This is because overriding the default on_message forbids commands from running
        # await self.bot.process_commands(message)

    @commands.slash_command(description="刪除N則訊息", dm_permission=False)
    @commands.default_member_permissions(administrator=True)
    async def clear(self, inter, num: int = commands.Param(name="n", ge=0)):
        self.bot_delete_edit = True
        await inter.channel.purge(limit=num + 1, bulk=True)  # 清除num+1則訊息
        self.bot_delete_edit = False

    @commands.slash_command(description="設定訊息刪除紀錄頻道", dm_permission=False)
    @commands.default_member_permissions(administrator=True)
    async def set_msg_delete_ch(self, inter,
                                channel_id: int = commands.Param(name="頻道id", description="輸入0以清除頻道設定",
                                                                 large=True)):
        guild = inter.guild
        answer = YesNoButton()

        if channel_id == 0:
            data[str(guild.id)]["msg_delete_channel_id"] = ""
            self.store_channel_data()
            await inter.response.send_message("已清除設定")
            return
        if guild.get_channel(channel_id) is None:
            await inter.response.send_message("找不到頻道")
            return
        if str(guild.id) in data:
            def check(i: disnake.MessageInteraction):
                return i.message.id == msg.id and i.author == inter.author

            if data[str(guild.id)]["msg_delete_channel_id"] != "":
                await inter.response.send_message("此伺服器已經設定過刪除訊息通知頻道\n是否要重新設置(y/n)",
                                                  view=answer)
                msg = await inter.original_response()
                await self.bot.wait_for(Event.button_click, check=check)
                if not answer.value:
                    return
            data[str(guild.id)]["msg_delete_channel_id"] = str(channel_id)
            self.store_channel_data()
        else:
            data[str(guild.id)] = {"msg_edit_channel_id": "", "msg_delete_channel_id": "", "non-listening_channel": []}
            data[str(guild.id)]["msg_delete_channel_id"] = str(channel_id)
            self.store_channel_data()
        if inter.response.is_done():
            await inter.followup.send("設置成功")
        else:
            await inter.response.send_message("設置成功")

    @commands.slash_command(description="設定訊息編輯紀錄頻道", dm_permission=False)
    @commands.default_member_permissions(administrator=True)
    async def set_msg_edit_ch(self, inter,
                              channel_id: int = commands.Param(name="頻道id", description="輸入0以清除頻道設定",
                                                               large=True)):
        guild = inter.guild
        answer = YesNoButton()

        if channel_id == 0:
            data[str(guild.id)]["msg_edit_channel_id"] = ""
            self.store_channel_data()
            await inter.response.send_message("已清除設定")
            return
        if guild.get_channel(channel_id) is None:
            await inter.response.send_message("找不到頻道")
            return
        if str(guild.id) in data:
            def check(i: disnake.MessageInteraction):
                return i.message.id == msg.id and i.author == inter.author

            if data[str(guild.id)]["msg_edit_channel_id"] != "":
                await inter.response.send_message("此伺服器已經設定過編輯訊息通知頻道\n是否要重新設置(y/n)",
                                                  view=answer)
                msg = await inter.original_response()
                await self.bot.wait_for(Event.button_click, check=check)
                if not answer.value:
                    return
            data[str(guild.id)]["msg_edit_channel_id"] = str(channel_id)
            self.store_channel_data()
        else:
            data[str(guild.id)] = {"msg_edit_channel_id": "", "msg_delete_channel_id": "", "non-listening_channel": []}
            data[str(guild.id)]["msg_edit_channel_id"] = str(channel_id)
            self.store_channel_data()
        if inter.response.is_done():
            await inter.followup.send("設置成功")
        else:
            await inter.response.send_message("設置成功")

    @commands.slash_command(description="設定*不監聽訊息編輯/刪除*頻道", dm_permission=False)
    @commands.default_member_permissions(administrator=True)
    async def set_non_listening_msg_ch(self, inter, channel_id: int = commands.Param(name="頻道id", large=True)):
        guild = inter.guild

        if guild.get_channel(channel_id) is None:
            await inter.response.send_message("找不到頻道")
            return
        if str(guild.id) in data:
            if str(channel_id) not in data[str(guild.id)]["non-listening_channel"]:
                data[str(guild.id)]["non-listening_channel"].append(str(channel_id))
                self.store_channel_data()
        else:
            data[str(guild.id)] = {"msg_edit_channel_id": "", "msg_delete_channel_id": "", "non-listening_channel": []}
            data[str(guild.id)]["non-listening_channel"].append(str(channel_id))
            self.store_channel_data()
        await inter.response.send_message("設置成功")

    @commands.slash_command(description="移除*不監聽訊息編輯/刪除*頻道", dm_permission=False)
    @commands.default_member_permissions(administrator=True)
    async def remove_non_listening_msg_ch(self, inter, channel_id: int = commands.Param(name="頻道id", large=True)):
        guild = inter.guild

        if str(guild.id) in data:
            if str(channel_id) in data[str(guild.id)]["non-listening_channel"]:
                data[str(guild.id)]["non-listening_channel"].remove(str(channel_id))
            else:
                await inter.response.send_message("頻道未被設定成不監聽")
                return
            self.store_channel_data()
            await inter.response.send_message("移除成功")
        else:
            data[str(guild.id)] = {"msg_edit_channel_id": "", "msg_delete_channel_id": "", "non-listening_channel": []}
            self.store_channel_data()
            await inter.response.send_message("頻道未被設定成不監聽")

    @commands.slash_command(description="列出訊息管理設定頻道", dm_permission=False)
    @commands.default_member_permissions(administrator=True)
    async def list_msg_manage_setting(self, inter):
        guild = inter.guild

        if str(guild.id) not in data:
            await inter.response.send_message("伺服器沒有設定訊息管理")
            return
        edit_ch = "None" if data[str(guild.id)]["msg_edit_channel_id"] == "" else "<#" + data[str(guild.id)]["msg_edit_channel_id"] + ">"
        del_ch = "None" if data[str(guild.id)]["msg_delete_channel_id"] == "" else "<#" + data[str(guild.id)]["msg_delete_channel_id"] + ">"
        if not data[str(guild.id)]["non-listening_channel"]:
            non_listen = "None"
        else:
            non_listen = ""
            for ch in data[str(guild.id)]["non-listening_channel"]:
                temp = "<#" + ch + ">\n"
                non_listen += temp
        t = timezone(timedelta(hours=8))
        timestamp = datetime.now(t)

        embed = disnake.Embed(title="Message manage setting", color=0x00bfff)
        embed.set_author(name=inter.author, icon_url=inter.author.avatar.url)
        embed.add_field(name="Message edit channel", value=edit_ch, inline=True)
        embed.add_field(name="Message delete channel", value=del_ch, inline=False)
        embed.add_field(name="Non-listening channel", value=non_listen, inline=False)
        embed.set_footer(text="\u200b")
        embed.timestamp = timestamp

        await inter.response.send_message(embed=embed)

    @commands.Cog.listener("on_raw_message_delete")
    async def msg_delete(self, payload: disnake.RawMessageDeleteEvent):
        if str(payload.guild_id) not in data:
            return
        del_ch = data[str(payload.guild_id)]["msg_delete_channel_id"]
        if del_ch == "" or del_ch == str(payload.channel_id):
            return
        if str(payload.channel_id) in data[str(payload.guild_id)]["non-listening_channel"]:
            return
        if self.bot_delete_edit:
            return
        guild = self.bot.get_guild(payload.guild_id)
        channel_id = int(data[str(payload.guild_id)]["msg_delete_channel_id"])
        channel = guild.get_channel(channel_id)
        if payload.cached_message is None:
            await channel.send(f"Message {payload.message_id} was be deleted in channel <#{payload.channel_id}>")
            return
        else:
            trigger_user = payload.cached_message.author
            msg = payload.cached_message

            async for entry in guild.audit_logs(action=disnake.AuditLogAction.message_delete,
                                                after=datetime.now(tz=timezone.utc) - timedelta(minutes=6)):
                if str(entry.id) not in AuditData.audit_data:
                    AuditData.audit_data[str(entry.id)] = {"count": entry.extra.count,
                                                           "created_at": entry.created_at,
                                                           "user": entry.user}
                    trigger_user = entry.user
                else:
                    if entry.extra.count != AuditData.audit_data[str(entry.id)]["count"]:
                        AuditData.audit_data[str(entry.id)]["count"] = entry.extra.count
                        trigger_user = AuditData.audit_data[str(entry.id)]["user"]
            if msg.attachments:  # list is not empty
                attachment = ""
                for e in msg.attachments:
                    attachment = attachment + "filename: " + e.filename + "\nurl: " + e.url + "\n"
                await channel.send(f"Attachment `{msg.author}`({msg.author.id}) send " +
                                   f"was deleted by `{trigger_user}`({trigger_user.id}) " +
                                   f"in channel <#{payload.channel_id}>\n" +
                                   attachment)
            else:
                await channel.send(f"A message `{msg.author}`({msg.author.id}) send " +
                                   f"was deleted by `{trigger_user}`({trigger_user.id}) " +
                                   f"in channel <#{payload.channel_id}>\n" +
                                   f"```{msg.content}```")

    @commands.Cog.listener("on_raw_message_edit")
    async def msg_edit(self, payload: disnake.RawMessageUpdateEvent):
        if str(payload.guild_id) not in data:
            return
        edit_ch = data[str(payload.guild_id)]["msg_edit_channel_id"]
        if edit_ch == "" or edit_ch == str(payload.channel_id):
            return
        if str(payload.channel_id) in data[str(payload.guild_id)]["non-listening_channel"]:
            return
        if self.bot_delete_edit or payload.cached_message.author == self.bot.user:
            return
        guild = self.bot.get_guild(payload.guild_id)
        channel_id = int(data[str(payload.guild_id)]["msg_edit_channel_id"])
        channel = guild.get_channel(channel_id)
        if payload.cached_message is None:
            await channel.send(f"Message {payload.message_id} was be edited in channel <#{payload.channel_id}>")
            return
        else:
            origin_msg = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
            msg = payload.cached_message
            await channel.send(f"A message `{msg.author}`({msg.author.id}) send " +
                               f"was be edited in channel <#{payload.channel_id}>\n" +
                               f"***before:***:\n```{msg.content}```" +
                               f"***\nafter:***\n```{origin_msg.content}```")

    @tasks.loop(minutes=10)
    async def clean_audit_variable(self):
        for key in list(AuditData.audit_data.keys()):
            if AuditData.audit_data[key]["created_at"] < datetime.now(tz=timezone.utc) - timedelta(minutes=6):
                AuditData.audit_data.pop(key)

    @commands.command()
    @commands.is_owner()
    async def print_audit_data(self, ctx):
        await ctx.send(str(AuditData.audit_data))


atexit.register(MsgManage.store_channel_data)


def setup(bot):
    bot.add_cog(MsgManage(bot))
