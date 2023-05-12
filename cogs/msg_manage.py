import disnake
from disnake.ext import commands, tasks
from core.any import CogExtension
from disnake import ui
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
        await interaction.response.send_message("確認更改")
        another_button = [x for x in self.children if x.custom_id == "n"][0]
        button.disabled = True
        another_button.disabled = True
        self.value = True

    @ui.button(label="No", style=disnake.ButtonStyle.red, custom_id="n")
    async def no_callback(self, button: ui.Button, interaction: disnake.Interaction):
        await interaction.response.send_message("確認取消")
        another_button = [x for x in self.children if x.custom_id == "y"][0]
        button.disabled = True
        another_button.disabled = True
        self.value = False


class MsgManage(CogExtension):
    def __init__(self, bot):
        super().__init__(bot)
        self.clean_audit_variable.start()
        self.bot_delete_edit = False     # whether is bot delete/edit message

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

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx, num: int):
        self.bot_delete_edit = True
        await ctx.channel.purge(limit=num + 1, bulk=True)  # 清除num+1則訊息
        self.bot_delete_edit = False

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_msg_delete_ch(self, ctx, channel_id: int):
        guild = ctx.guild
        answer = YesNoButton()

        if str(guild.id) in data:
            if data[str(guild.id)]["msg_delete_channel_id"] != "":
                await ctx.send("此伺服器已經設定過刪除訊息通知頻道\n是否要重新設置(y/n)", view=answer)
                if not answer.value:
                    return
            data[str(guild.id)]["msg_delete_channel_id"] = str(channel_id)
            self.store_channel_data()
        else:
            data[str(guild.id)] = {"msg_edit_channel_id": "", "msg_delete_channel_id": ""}
            data[str(guild.id)]["msg_delete_channel_id"] = str(channel_id)
            self.store_channel_data()
        await ctx.send("設置成功")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_msg_edit_ch(self, ctx, channel_id: int):
        guild = ctx.guild
        answer = YesNoButton()

        if str(guild.id) in data:
            if data[str(guild.id)]["msg_edit_channel_id"] != "":
                await ctx.send("此伺服器已經設定過編輯訊息通知頻道\n是否要重新設置(y/n)", view=answer)
                if not answer.value:
                    return
            data[str(guild.id)]["msg_edit_channel_id"] = str(channel_id)
            self.store_channel_data()
        else:
            data[str(guild.id)] = {"msg_edit_channel_id": "", "msg_delete_channel_id": ""}
            data[str(guild.id)]["msg_edit_channel_id"] = str(channel_id)
            self.store_channel_data()
        await ctx.send("設置成功")

    @commands.Cog.listener("on_raw_message_delete")
    async def msg_delete(self, payload: disnake.RawMessageDeleteEvent):
        if str(payload.guild_id) not in data:
            return
        del_ch = data[str(payload.guild_id)]["msg_delete_channel_id"]
        if del_ch == "" or del_ch == str(payload.channel_id):
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
        if self.bot_delete_edit:
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
    async def print_audit_data(self, ctx):
        await ctx.send(str(AuditData.audit_data))


atexit.register(MsgManage.store_channel_data)


def setup(bot):
    bot.add_cog(MsgManage(bot))
