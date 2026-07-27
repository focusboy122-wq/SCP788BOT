from telegram import Update
from telegram.ext import ContextTypes

from db import database as db


async def reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await db.upsert_user(user.id, user.username)

    arg = context.args[0].lower() if context.args else None

    if arg not in ("on", "off"):
        await update.message.reply_text(
            "Usage: /reminders on  — or  /reminders off\n"
            "When on, you'll get a message ~30 minutes before kickoff for teams you follow."
        )
        return

    await db.set_reminders(user.id, enabled=(arg == "on"))
    state = "on \u2705" if arg == "on" else "off"
    await update.message.reply_text(f"Kickoff reminders turned {state}.")
