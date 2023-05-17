import disnake
from disnake import ui, Event
from disnake.ext import commands
from core.any import CogExtension
import json
import atexit

with open("json/member_welcome.json", "r") as file:
    data = json.load(file)


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


class Member(CogExtension):
    @staticmethod
    def store_channel_data():
        with open("json/member_welcome.json", "w") as f:
            json.dump(data, f, indent=4)

    @commands.slash_command(description="取得成員頭像")
    async def avatar(self, inter, user: disnake.Member = commands.Param(name="成員", default=None)):
        avatar_imgs = []
        if user is None:
            avatar_imgs.append(await inter.author.avatar.to_file())
            if inter.author.avatar.url != inter.author.display_avatar.url:
                avatar_imgs.append(await inter.author.display_avatar.to_file())
            await inter.response.send_message(f"{inter.author.name}的頭貼:", files=avatar_imgs)
        else:
            avatar_imgs.append(await user.avatar.to_file())
            if user.avatar.url != user.display_avatar.url:
                avatar_imgs.append(await user.display_avatar.to_file())
            await inter.response.send_message(f"{user.name}的頭貼:", files=avatar_imgs)

    @commands.slash_command(description="設定成員加入訊息頻道", dm_permission=False)
    @commands.default_member_permissions(administrator=True)
    async def set_join_ch(self, inter, channel_id: int = commands.Param(name="頻道id", large=True)):
        guild = inter.guild
        answer = YesNoButton()

        if str(guild.id) in data:
            def check(i: disnake.MessageInteraction):
                return i.message.id == msg.id and i.author == inter.author

            if data[str(guild.id)]["member_join_channel"] != "":
                await inter.response.send_message("此伺服器已經設定過成員加入通知頻道\n是否要重新設置(y/n)", view=answer)
                msg = await inter.original_response()
                await self.bot.wait_for(Event.button_click, check=check)
                if not answer.value:
                    return
            data[str(guild.id)]["member_join_channel"] = str(channel_id)
            self.store_channel_data()
        else:
            data[str(guild.id)] = {"member_join_channel": "", "member_remove_channel": ""}
            data[str(guild.id)]["member_join_channel"] = str(channel_id)
            self.store_channel_data()
        if inter.response.is_done():
            await inter.followup.send("設置成功")
        else:
            await inter.response.send_message("設置成功")

    @commands.slash_command(description="設定成員離開訊息頻道", dm_permission=False)
    @commands.default_member_permissions(administrator=True)
    async def set_remove_ch(self, inter, channel_id: int = commands.Param(name="頻道id", large=True)):
        guild = inter.guild
        answer = YesNoButton()

        if str(guild.id) in data:
            def check(i: disnake.MessageInteraction):
                return i.message.id == msg.id and i.author == inter.author

            if data[str(guild.id)]["member_remove_channel"] != "":
                await inter.response.send_message("此伺服器已經設定過成員離開通知頻道\n是否要重新設置(y/n)", view=answer)
                msg = await inter.original_response()
                await self.bot.wait_for(Event.button_click, check=check)
                if not answer.value:
                    return
            data[str(guild.id)]["member_remove_channel"] = str(channel_id)
            self.store_channel_data()
        else:
            data[str(guild.id)] = {"member_join_channel": "", "member_remove_channel": ""}
            data[str(guild.id)]["member_remove_channel"] = str(channel_id)
            self.store_channel_data()
        if inter.response.is_done():
            await inter.followup.send("設置成功")
        else:
            await inter.response.send_message("設置成功")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        if str(guild.id) not in data:
            return
        elif data[str(guild.id)]["member_join_channel"] == "":
            return
        await self.bot.get_channel(int(data[str(guild.id)]["member_join_channel"])).send(f"Welcome <@{member.id}>!")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        if str(guild.id) not in data:
            return
        elif data[str(guild.id)]["member_remove_channel"] == "":
            return
        await self.bot.get_channel(int(data[str(guild.id)]["member_remove_channel"])).send(f"Bye <@{member.id}>!")


atexit.register(Member.store_channel_data)


def setup(bot):
    bot.add_cog(Member(bot))
