import disnake
from disnake import Event, ui
from disnake.ext import commands
from core.any import CogExtension
import asyncio
import json
import atexit
import datetime

role_msg_data = {}

with open("json/role_msg.json", "r") as f:
    role_msg_data = json.load(f)


class Role(CogExtension):
    @staticmethod
    def store_reaction_roles():
        with open("json/role_msg.json", "w") as file:
            json.dump(role_msg_data, file, indent=4)

    @commands.slash_command(description="設置反應身分組", dm_permission=False)
    @commands.default_member_permissions(administrator=True)
    async def set_role(self, inter):
        author = inter.author
        channel = inter.channel
        guild = inter.guild

        def check(m):
            return m.channel == channel and m.author == author

        try:
            await inter.response.send_message("輸入要設定反應給予身分組的頻道ID")
            channel_id = await self.bot.wait_for(Event.message, check=check, timeout=60)
            await inter.followup.send("輸入要設定反應給予身分組的訊息ID")
            msg_id = await self.bot.wait_for(Event.message, check=check, timeout=60)
            await inter.followup.send("輸入要設定反應給予身分組的表符(先輸入\\\\再按表符)")
            emoji = await self.bot.wait_for(Event.message, check=check, timeout=60)
            await inter.followup.send("輸入要設定反應給予身分組的身分組ID")
            role_id = await self.bot.wait_for(Event.message, check=check, timeout=60)
        except asyncio.TimeoutError:
            await inter.followup.send("已超過時間,請重新輸入指令")
            return
        channel_id = channel_id.content
        msg_channel = guild.get_channel(int(channel_id))
        if msg_channel is None:
            await inter.followup.send("找不到頻道,請確認頻道ID是否輸入正確")
            return
        msg_id = msg_id.content
        try:
            await msg_channel.fetch_message(int(msg_id))
        except disnake.NotFound:
            await inter.followup.send("找不到訊息,請確認訊息ID是否正確")
            return
        except disnake.Forbidden:
            await inter.followup.send("無法取得訊息,請確認機器人是否在該訊息的頻道有權限")
            return
        except disnake.HTTPException:
            await inter.followup.send("訊息檢索失敗")
            return
        emoji_id = emoji.content.split(":")[2]
        emoji_id = emoji_id[: -1]
        emoji_name = emoji.content.split(":")[1]
        # 以下程式碼會無法使用其他伺服器的表符作為獲得身分組的依據
        # 但單純做判斷可以使用其他伺服器表符
        # try:
        #     await guild.fetch_emoji(emoji_id)
        # except disnake.NotFound:
        #     await ctx.send("找不到表符,請再確認表符是否存在於伺服器或為預設表符")
        #     return
        # except disnake.HTTPException:
        #     await ctx.send("表符檢索失敗")
        #     return
        role_id = role_id.content
        role = guild.get_role(int(role_id))
        if role is None:
            await inter.followup.send("找不到身分組,請確認身分組ID是否正確")
            return
        # record data in global variable and write in json
        if str(guild.id) not in role_msg_data:
            role_msg_data[str(guild.id)] = []
        role_msg_data[str(guild.id)].append(
            {
                "msg_channel": channel_id,
                "msg_id": msg_id,
                "emoji_name": emoji_name,
                "emoji_id": emoji_id,
                "role_id": role_id
            }
        )
        self.store_reaction_roles()
        await inter.followup.send("新增成功")

    @commands.slash_command(description="查詢有哪些反應身分組")
    async def list_role_msg(self, inter):
        guild = inter.guild
        with open("json/role_msg.json", "r") as f:
            data = json.load(f)
        if str(guild.id) not in data:
            await inter.response.send_message("目前沒有資料")
            return
        data = data[str(guild.id)]
        max_page = len(data)
        now_page = 0
        t = datetime.timezone(datetime.timedelta(hours=8))
        timestamp = datetime.datetime.now(t)

        def update_embed():
            nonlocal now_page, max_page, timestamp
            link = "https://discord.com/channels/" + str(guild.id) + "/" + data[now_page]["msg_channel"] + "/" + \
                   data[now_page]["msg_id"]
            emoji = "<:" + data[now_page]["emoji_name"] + ":" + data[now_page]["emoji_id"] + ">"
            role = "<@&" + data[now_page]["role_id"] + ">"
            embed = disnake.Embed(title="Role message list",
                                  description="(" + str(now_page + 1) + "/" + str(max_page) + ")",
                                  color=0x00bfff)
            embed.set_author(name=inter.author, icon_url=inter.author.avatar.url)
            embed.add_field(name="Message link", value=link, inline=True)
            embed.add_field(name="Emoji", value=emoji, inline=False)
            embed.add_field(name="Role", value=role, inline=False)
            embed.set_footer(text="\u200b")
            embed.timestamp = timestamp
            return embed

        previous_btn = ui.Button(label="上一頁", disabled=True)
        next_btn = ui.Button(label="下一頁", disabled=True if max_page == 1 else False)

        async def previous_page(interaction: disnake.Interaction):
            nonlocal now_page, max_page, view
            now_page -= 1
            next_btn.disabled = False
            if now_page == 0:
                previous_btn.disabled = True
            await interaction.response.edit_message(embed=update_embed(), view=view)

        async def next_page(interaction: disnake.Interaction):
            nonlocal now_page, max_page, view
            now_page += 1
            previous_btn.disabled = False
            if now_page + 1 == max_page:
                next_btn.disabled = True
            await interaction.response.edit_message(embed=update_embed(), view=view)

        previous_btn.callback = previous_page
        next_btn.callback = next_page
        view = ui.View()
        view.add_item(previous_btn)
        view.add_item(next_btn)
        await inter.response.send_message(embed=update_embed(), view=view)

    @commands.Cog.listener("on_raw_reaction_add")
    async def add_role(self, payload: disnake.RawReactionActionEvent):
        guild_id = str(payload.guild_id)
        data = role_msg_data.get(guild_id)
        if not (data is None):
            for d in data:
                if d["msg_channel"] == str(payload.channel_id):
                    if d["msg_id"] == str(payload.message_id):
                        if d["emoji_id"] == str(payload.emoji.id):
                            guild = self.bot.get_guild(payload.guild_id)
                            member = guild.get_member(payload.user_id)
                            await member.add_roles(guild.get_role(int(d["role_id"])))

    @commands.Cog.listener("on_raw_reaction_remove")
    async def remove_role(self, payload: disnake.RawReactionActionEvent):
        guild_id = str(payload.guild_id)
        data = role_msg_data.get(guild_id)
        if not (data is None):
            for d in data:
                if d["msg_channel"] == str(payload.channel_id):
                    if d["msg_id"] == str(payload.message_id):
                        if d["emoji_id"] == str(payload.emoji.id):
                            guild = self.bot.get_guild(payload.guild_id)
                            member = guild.get_member(payload.user_id)
                            await member.remove_roles(guild.get_role(int(d["role_id"])))


atexit.register(Role.store_reaction_roles)


def setup(bot):
    bot.add_cog(Role(bot))
