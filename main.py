from disnake.ext import commands
import disnake
import os
from util.audit_var import AuditData
from dotenv import load_dotenv
import keep_alive

load_dotenv()

intents = disnake.Intents.all()
bot = commands.Bot(command_prefix="sudo! ", intents=intents, owner_id=int(os.getenv("OWNER_ID")))


@bot.event
async def on_ready():
    await AuditData.init_audit_date(bot)
    print("Bot is on ready!")


@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.bot.close()


for file in os.listdir("cogs"):
    if file.endswith(".py"):
        cog_name = file[:-3]
        bot.load_extension(f"cogs.{cog_name}")

keep_alive.keep_alive()
bot.run(os.getenv("BOT_TOKEN"))
