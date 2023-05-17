import disnake
from disnake.ext import commands
from core.any import CogExtension


class EmbedHelp(CogExtension):
    @commands.slash_command(description="取得指令說明")
    async def helping(self, inter):
        embed = disnake.Embed(title="指令", description="來看看有什麼指令", color=0x7e00c2)
        embed.add_field(name="sudo! clear", value="刪除n個訊息", inline=False)
        embed.add_field(name="sudo! a", value="A", inline=False)
        embed.add_field(name="sudo! hello", value="嗨", inline=False)
        await inter.response.send_message(embed=embed)


def setup(bot):
    bot.add_cog(EmbedHelp(bot))
