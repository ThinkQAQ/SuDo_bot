from disnake.ext import commands
from util.bank_sys import BankSys
from core.any import CogExtension
import random
import asyncio


class Game(CogExtension):
    @commands.slash_command(description="賭博啦", dm_permission=False)
    async def slots(
            self, inter,
            amount: int = commands.Param(name="金額", gt=0),
            mul: int = commands.Param(name="倍率", gt=0)
    ):
        BankSys.open_account(inter.author)
        balance = BankSys.get_user_bank_data(inter.author)
        amount = amount
        mul = mul
        if balance["wallet"] <= 0:
            await inter.response.send_message("你沒錢啦")
            return
        if balance["wallet"] < amount:
            await inter.response.send_message("你錢不夠啦")
            return
        if amount * mul > 2000:
            await inter.response.send_message("下注太多了,我賠不起! 最高下注金額*倍率=2000!")
            return

        final = []
        for _ in range(3):
            temp = random.choice(["X", "Q", "O"])
            final.append(temp)
        win = amount * mul
        loss = amount * mul * -1
        await inter.response.send_message("Spinning...")
        await asyncio.sleep(3)
        await inter.edit_original_response(str(final))
        # win
        if final[0] == final[1] == final[2]:
            BankSys.update_bank(inter.author, win, "wallet")
            await inter.followup.send(f"你贏了{win}塊錢")
        # loss
        else:
            BankSys.update_bank(inter.author, loss, "wallet")
            await inter.followup.send(f"你輸了{win}塊錢")


def setup(bot):
    bot.add_cog(Game(bot))
