import disnake
from disnake.ext import commands
from core.any import CogExtension
from datetime import timedelta


class MemManage(CogExtension):
    @commands.slash_command(description="禁言成員,最大支持27:23:59:59", dm_permission=False)
    @commands.default_member_permissions(moderate_members=True)
    async def mute(
            self, inter,
            member: disnake.Member = commands.Param(name="成員"),
            days: commands.Range[0, 27] = commands.Param(name="天", default=0),
            hours: commands.Range[0, 23] = commands.Param(name="時", default=0),
            minutes: commands.Range[0, 59] = commands.Param(name="分", default=0),
            seconds: commands.Range[0, 59] = commands.Param(name="秒", default=0),
            reason: str = commands.Param(name="原因", default="沒有提供原因")
    ):
        if member.guild_permissions.administrator or member.guild_permissions.moderate_members:
            await inter.response.send_message("你沒有權限禁言此成員")
            return
        guild = inter.guild
        duration = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        await member.send(f"你在 {guild.name} 已被禁言{days}天{hours}時{minutes}分{seconds}秒, 原因:{reason}")
        await inter.response.send_message(
            f"成員 <@{member.id}> 已被禁言{days}天{hours}時{minutes}分{seconds}秒, 原因:{reason}")
        await guild.timeout(user=member, duration=duration, reason=reason)

    @commands.slash_command(description="將成員踢出伺服器", dm_permission=False)
    @commands.default_member_permissions(kick_members=True)
    async def kick(
            self, inter,
            member: disnake.Member = commands.Param(name="成員"),
            reason: str = commands.Param(name="原因", default="沒有提供原因")
    ):
        if member.guild_permissions.administrator or member.guild_permissions.kick_members:
            await inter.response.send_message("你沒有權限將此成員踢出伺服器")
            return
        guild = inter.guild
        await member.send(f"你已被踢出 {guild.name} , 原因:{reason}")
        await inter.response.send_message(f"成員 <@{member.id}> 已被踢出伺服器, 原因:{reason}")
        await guild.kick(user=member, reason=reason)

    @commands.slash_command(description="在此伺服器停權成員", dm_permission=False)
    @commands.default_member_permissions(ban_members=True)
    async def ban(
            self, inter,
            member: disnake.Member = commands.Param(name="成員"),
            duration: commands.Range[0, 7] = commands.Param(name="刪除訊息", description="是否刪除該用戶所發送的訊息, 此參數為刪除幾天的訊息, 預設不刪除訊息", default=0),
            reason: str = commands.Param(name="原因", default="沒有提供原因")
    ):
        if member.guild_permissions.administrator or member.guild_permissions.ban_members:
            await inter.response.send_message("你沒有權限停權此成員")
            return
        guild = inter.guild
        await member.send(f"你在 {guild.name} 已被停權, 原因:{reason}")
        await inter.response.send_message(f"成員 <@{member.id}> 已被停權, 原因:{reason}")
        await guild.ban(user=member, clean_history_duration=duration, reason=reason)

    @commands.slash_command(description="在此伺服器解除成員停權", dm_permission=False)
    @commands.default_member_permissions(ban_members=True)
    async def unban(
            self, inter,
            user_id: int = commands.Param(name="使用者id", large=True),
            reason: str = commands.Param(name="原因", default="沒有提供原因")
    ):
        guild = inter.guild
        async for banned in guild.bans():
            if banned.user.id == user_id:
                await guild.unban(user=banned.user, reason=reason)
                await inter.response.send_message(f"成員 <@{banned.user.id}> 已被解除停權, 原因:{reason}")
                return
        await inter.response.send_message("找不到成員")


def setup(bot):
    bot.add_cog(MemManage(bot))
