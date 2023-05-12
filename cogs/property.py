import disnake
from disnake.ext import commands
from util.bank_sys import BankSys
from core.any import CogExtension
import random
import json

shop = [
    {"name": "Watch", "price": 8},
    {"name": "Laptop", "price": 87},
    {"name": "PC", "price": 870},
    {"name": "PS5", "price": 690},
    {"name": "Cat", "price": 1000}
]


class Money(CogExtension):
    @commands.command()
    async def money(self, ctx):
        user = ctx.author
        BankSys.open_account(user)
        users = BankSys.get_bank_data()
        wallet = users[str(user.id)]["wallet"]
        bank = users[str(user.id)]["bank"]
        embed = disnake.Embed(title=f"{user.name}'s 錢包", color=disnake.Color.red())
        embed.set_thumbnail(url=user.avatar)
        embed.add_field(name="Wallet", value=wallet, inline=True)
        embed.add_field(name="Bank", value=bank, inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def market(self, ctx):
        embed = disnake.Embed(title="Market", colour=disnake.Color.blurple())

        for item in shop:
            name = item["name"]
            price = item["price"]
            embed.add_field(name=name, value=f"${price}", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def beg(self, ctx):
        user = ctx.author
        BankSys.open_account(user)
        users = BankSys.get_bank_data()

        earning = random.randint(1, 100)
        await ctx.send(f"某人給了你{earning}塊錢")
        users[str(user.id)]["wallet"] += earning

        with open("json/bank.json", "w") as f:
            json.dump(users, f, indent=4)

    @commands.command()
    async def withdraw(self, ctx, amount=None):
        BankSys.open_account(ctx.author)
        if amount is None:
            await ctx.send("請輸入數字")
            return
        balance = BankSys.get_user_bank_data(ctx.author)
        amount = int(amount)
        if balance["bank"] < amount:
            await ctx.send("你的銀行戶頭沒那麼多錢")
            return
        if amount < 0:
            await ctx.send("負數???????")
            return
        BankSys.update_bank(ctx.author, amount, "wallet")
        BankSys.update_bank(ctx.author, amount * -1, "bank")
        await ctx.send(f"你提款了{amount}塊錢")

    @commands.command()
    async def deposit(self, ctx, amount=None):
        BankSys.open_account(ctx.author)
        if amount is None:
            await ctx.send("請輸入數字")
            return
        balance = BankSys.get_user_bank_data(ctx.author)
        amount = int(amount)
        if balance["bank"] < amount:
            await ctx.send("你的錢包沒那麼多錢")
            return
        if amount < 0:
            await ctx.send("負數???????")
            return
        BankSys.update_bank(ctx.author, amount * -1, "wallet")
        BankSys.update_bank(ctx.author, amount, "bank")
        await ctx.send(f"你存款了{amount}塊錢")

    @commands.command()
    async def remit(self, ctx, member: disnake.Member, amount=None):
        BankSys.open_account(ctx.author)
        BankSys.open_account(member)
        if amount is None:
            await ctx.send("請輸入數字")
            return
        balance = BankSys.get_user_bank_data(ctx.author)
        if amount == "all":
            amount = balance["bank"]
        amount = int(amount)
        if balance["bank"] < amount:
            await ctx.send("你的銀行戶頭沒那麼多錢")
            return
        if amount < 0:
            await ctx.send("負數???????")
            return
        BankSys.update_bank(ctx.author, amount * -1, "bank")
        BankSys.update_bank(member, amount, "bank")
        await ctx.send(f"<@{ctx.author.id}> 匯給了 <@{member.id}> {amount}塊錢")

    @commands.command()
    async def bag(self, ctx):
        BankSys.open_account(ctx.author)
        users = BankSys.get_bank_data()
        bag = users[str(ctx.author.id)]["bag"]
        embed = disnake.Embed(title="Bag", color=0xFF5733)
        embed.set_thumbnail(url=ctx.author.avatar)
        for item in bag:
            name = item["item"]
            amount = item["amount"]
            embed.add_field(name=name, value=amount)

        await ctx.send(embed=embed)

    @commands.command()
    async def buy(self, ctx, item, amount=1):
        BankSys.open_account(ctx.author)
        result = buy_something(ctx.author, item, amount)
        if result[0] == False:
            if result[1] == 1:
                await ctx.send("沒有這個東西")
                return
            if result[1] == 2:
                await ctx.send(f"你錢包裡的錢不夠購買{amount}個{item}")
                return
        await ctx.send(f"你購買了{amount}個{item}")


def buy_something(user, item_name, amount):
    name = None
    item_name = item_name.lower()
    for item in shop:
        shop_item_name = item["name"].lower()
        if item_name == shop_item_name:
            name = item_name
            price = item["price"]
            break
    if name is None:
        return [False, 1]
    cost = price * amount
    users = BankSys.get_bank_data()
    balance = BankSys.get_user_bank_data(user)
    if balance["wallet"] < cost:
        return [False, 2]

    count = 0
    exist = 0
    for belongings in users[str(user.id)]["bag"]:
        if item_name == belongings["item"]:
            users[str(user.id)]["bag"][count]["amount"] = users[str(user.id)]["bag"][count]["amount"] + amount
            exist = 1
            break
        count += 1
    if exist == 0:
        new = {"item": item_name, "amount": amount}
        users[str(user.id)]["bag"].append(new)
    with open("json/bank.json", "w") as f:
        json.dump(users, f, indent=4)
    BankSys.update_bank(user, cost * -1, "wallet")
    return [True, "worked"]


def setup(bot):
    bot.add_cog(Money(bot))
