# language: Python, file: bot.py
# Бот-агрегатор прошивок Nintendo. Тянет последние релизы с GitHub.
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8967369146:AAFuFbDzLVNAPNgXSlDMU4zYuoXzDG2rwls"

REPOS = {
    "switch_cfw": "zanytofu/nxcfw",
    "switch_fw": "THZoria/NX_Firmware",
    "switch_tfos": "Team-Failure/TF-OS",
    "switch_4ifir": "rashevskyv/4IFIR",
    "3ds_luma": "LumaTeam/Luma3DS",
}

async def get_latest_release(repo: str):
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(f"https://api.github.com/repos/{repo}/releases/latest")
        if r.status_code != 200:
            return None
        data = r.json()
        return {
            "tag": data.get("tag_name", "?"),
            "url": data.get("html_url", ""),
            "published": data.get("published_at", "?")[:10],
        }

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Nintendo CFW Bot\n\n"
        "/switch - CFW для Switch\n"
        "/3ds - CFW для 3DS\n"
        "/firmware - свежая прошивка Switch\n"
        "/sources - источники"
    )

async def cmd_switch(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = "Nintendo Switch CFW:\n\n"
    for name, repo in REPOS.items():
        if "switch" not in name:
            continue
        rel = await get_latest_release(repo)
        if rel:
            msg += f"{repo} - {rel['tag']} ({rel['published']})\n{rel['url']}\n\n"
    await update.message.reply_text(msg, disable_web_page_preview=True)

async def cmd_3ds(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = "Nintendo 3DS CFW:\n\n"
    for name, repo in REPOS.items():
        if "3ds" not in name:
            continue
        rel = await get_latest_release(repo)
        if rel:
            msg += f"{repo} - {rel['tag']} ({rel['published']})\n{rel['url']}\n\n"
    await update.message.reply_text(msg, disable_web_page_preview=True)

async def cmd_firmware(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    rel = await get_latest_release(REPOS["switch_fw"])
    if rel:
        msg = f"Switch Firmware - {rel['tag']}\n{rel['url']}"
        await update.message.reply_text(msg, disable_web_page_preview=True)
    else:
        await update.message.reply_text("Нет данных.")

async def cmd_sources(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = "Источники:\n\n"
    for name, repo in REPOS.items():
        msg += f"{repo}\n"
    await update.message.reply_text(msg)

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("switch", cmd_switch))
    app.add_handler(CommandHandler("3ds", cmd_3ds))
    app.add_handler(CommandHandler("firmware", cmd_firmware))
    app.add_handler(CommandHandler("sources", cmd_sources))
    app.run_polling()
