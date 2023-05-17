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
shop_item = [x["name"] for x in shop]


class Money(CogExtension):
    @commands.slash_command(description="查詢錢包", dm_permission=False)
    async def money(self, inter):
        user = inter.author
        BankSys.open_account(user)
        users = BankSys.get_bank_data()
        wallet = users[str(user.id)]["wallet"]
        bank = users[str(user.id)]["bank"]
        embed = disnake.Embed(title=f"{user.name}'s 錢包", color=disnake.Color.red())
        embed.set_thumbnail(url=user.avatar)
        embed.add_field(name="Wallet", value=wallet, inline=True)
        embed.add_field(name="Bank", value=bank, inline=True)
        await inter.response.send_message(embed=embed)

    @commands.slash_command(description="查詢市場", dm_permission=False)
    async def market(self, inter):
        embed = disnake.Embed(title="Market", colour=disnake.Color.blurple())

        for item in shop:
            name = item["name"]
            price = item["price"]
            embed.add_field(name=name, value=f"${price}", inline=False)
        await inter.response.send_message(embed=embed)

    @commands.slash_command(description="跟別人乞討錢錢", dm_permission=False)
    async def beg(self, inter):
        user = inter.author
        BankSys.open_account(user)
        users = BankSys.get_bank_data()

        earning = random.randint(1, 100)
        await inter.response.send_message(f"某人給了你{earning}塊錢")
        users[str(user.id)]["wallet"] += earning

        with open("json/bank.json", "w") as f:
            json.dump(users, f, indent=4)

    @commands.slash_command(description="提款", dm_permission=False)
    async def withdraw(self, inter, amount: int = commands.Param(name="金額", gt=0)):
        BankSys.open_account(inter.author)
        balance = BankSys.get_user_bank_data(inter.author)
        if balance["bank"] < amount:
            await inter.response.send_message("你的銀行戶頭沒那麼多錢")
            return
        BankSys.update_bank(inter.author, amount, "wallet")
        BankSys.update_bank(inter.author, amount * -1, "bank")
        await inter.response.send_message(f"你提款了{amount}塊錢")

    @commands.slash_command(description="存款", dm_permission=False)
    async def deposit(self, inter, amount: int = commands.Param(name="金額", gt=0)):
        BankSys.open_account(inter.author)
        balance = BankSys.get_user_bank_data(inter.author)
        if balance["wallet"] < amount:
            await inter.response.send_message("你的錢包沒那麼多錢")
            return
        BankSys.update_bank(inter.author, amount * -1, "wallet")
        BankSys.update_bank(inter.author, amount, "bank")
        await inter.response.send_message(f"你存款了{amount}塊錢")

    @commands.slash_command(description="匯錢給別人", dm_permission=False)
    async def remit(
            self, inter,
            member: disnake.Member = commands.Param(name="用戶"),
            amount: int = commands.Param(name="金額", gt=0)
    ):
        BankSys.open_account(inter.author)
        BankSys.open_account(member)

        balance = BankSys.get_user_bank_data(inter.author)
        if balance["bank"] < amount:
            await inter.response.send_message("你的銀行戶頭沒那麼多錢")
            return
        BankSys.update_bank(inter.author, amount * -1, "bank")
        BankSys.update_bank(member, amount, "bank")
        await inter.response.send_message(f"<@{inter.author.id}> 匯給了 <@{member.id}> {amount}塊錢")

    @commands.slash_command(description="查詢包包", dm_permission=False)
    async def bag(self, inter):
        BankSys.open_account(inter.author)
        users = BankSys.get_bank_data()
        bag = users[str(inter.author.id)]["bag"]
        embed = disnake.Embed(title="Bag", color=0xFF5733)
        embed.set_thumbnail(url=inter.author.avatar)
        for item in bag:
            name = item["item"]
            amount = item["amount"]
            embed.add_field(name=name, value=amount)

        await inter.response.send_message(embed=embed)

    @commands.slash_command(description="買買買", dm_permission=False)
    async def buy(
            self, inter,
            item: str = commands.Param(name="商品", choices=shop_item),
            amount: int = commands.Param(name="數量", gt=0)
    ):
        BankSys.open_account(inter.author)
        result = buy_something(inter.author, item, amount)
        if result[0] == False:
            if result[1] == 2:
                await inter.response.send_message(f"你錢包裡的錢不夠購買{amount}個{item}")
                return
        await inter.response.send_message(f"你購買了{amount}個{item}")


def buy_something(user, item_name, amount):
    for item in shop:
        shop_item_name = item["name"]
        if item_name == shop_item_name:
            price = item["price"]
            break
    cost = price * amount
    users = BankSys.get_bank_data()
    balance = BankSys.get_user_bank_data(user)
    if balance["wallet"] < cost:
        return [False, 1]

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
