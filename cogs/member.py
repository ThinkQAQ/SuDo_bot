import disnake
from disnake import ui
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


class Member(CogExtension):
    @staticmethod
    def store_channel_data():
        with open("json/member_welcome.json", "w") as f:
            json.dump(data, f, indent=4)

    @commands.command()
    async def avatar(self, ctx, user=None):
        avatar_imgs = []
        if user is None:
            avatar_imgs.append(await ctx.author.avatar.to_file())
            if ctx.author.avatar.url != ctx.author.display_avatar.url:
                avatar_imgs.append(await ctx.author.display_avatar.to_file())
            await ctx.send(f"{ctx.author.name}的頭貼:", files=avatar_imgs)
        else:
            guild = ctx.guild
            user = guild.get_member(int(user[2:-1]))
            avatar_imgs.append(await user.avatar.to_file())
            if user.avatar.url != user.display_avatar.url:
                avatar_imgs.append(await user.display_avatar.to_file())
            await ctx.send(f"{user.name}的頭貼:", files=avatar_imgs)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_join_ch(self, ctx, channel_id: int):
        guild = ctx.guild
        answer = YesNoButton()

        if str(guild.id) in data:
            if data[str(guild.id)]["member_join_channel"] != "":
                await ctx.send("此伺服器已經設定過成員加入通知頻道\n是否要重新設置(y/n)", view=answer)
                if not answer.value:
                    return
            data[str(guild.id)]["member_join_channel"] = str(channel_id)
            self.store_channel_data()
        else:
            data[str(guild.id)] = {"member_join_channel": "", "member_remove_channel": ""}
            data[str(guild.id)]["member_join_channel"] = str(channel_id)
            self.store_channel_data()
        await ctx.send("設置成功")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_remove_ch(self, ctx, channel_id: int):
        guild = ctx.guild
        answer = YesNoButton()

        if str(guild.id) in data:
            if data[str(guild.id)]["member_remove_channel"] != "":
                await ctx.send("此伺服器已經設定過成員離開通知頻道\n是否要重新設置(y/n)", view=answer)
                if not answer.value:
                    return
            data[str(guild.id)]["member_remove_channel"] = str(channel_id)
            self.store_channel_data()
        else:
            data[str(guild.id)] = {"member_join_channel": "", "member_remove_channel": ""}
            data[str(guild.id)]["member_remove_channel"] = str(channel_id)
            self.store_channel_data()
        await ctx.send("設置成功")

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
