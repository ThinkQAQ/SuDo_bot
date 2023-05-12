from disnake.ext import commands
from util.bank_sys import BankSys
from core.any import CogExtension
import random
import asyncio


class Game(CogExtension):
    @commands.command()
    async def slots(self, ctx, amount=None, mul=None):
        BankSys.open_account(ctx.author)
        if mul is None:
            await ctx.send("請輸入倍率")
            return
        balance = BankSys.get_user_bank_data(ctx.author)
        amount = int(amount)
        mul = int(mul)
        if balance["wallet"] <= 0:
            await ctx.send("你沒錢啦")
            return
        if balance["wallet"] < amount:
            await ctx.send("你錢不夠啦")
            return
        if amount < 0:
            await ctx.send("下注負數???")
            return
        if amount == 0:
            await ctx.send("下注0? 不要玩我")
            return
        if amount * mul > 2000:
            await ctx.send("下注太多了,我賠不起! 最高下注金額*倍率=2000!")

        final = []
        for _ in range(3):
            temp = random.choice(["X", "Q", "O"])
            final.append(temp)
        win = amount * mul
        loss = amount * mul * -1
        await ctx.send("Spinning...")
        await asyncio.sleep(3)
        await ctx.send(str(final))
        # win
        if final[0] == final[1] == final[2]:
            BankSys.update_bank(ctx.author, win, "wallet")
            await ctx.send(f"你贏了{win}塊錢")
        # loss
        else:
            BankSys.update_bank(ctx.author, loss, "wallet")
            await ctx.send(f"你輸了{win}塊錢")


def setup(bot):
    bot.add_cog(Game(bot))
