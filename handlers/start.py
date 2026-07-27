from telegram import Update
from telegram.ext import ContextTypes

from db import database as db

WELCOME = (
    "\U0001F3C6 *Welcome to SCP788BOT!*\n\n"
    "Your free daily sports companion — live scores, fixtures, standings "
    "and news for the teams you follow, right here in Telegram.\n\n"
    "Let's get you set up:\n"
    "1\uFE0F\u20E3 Use /follow <team name> to add a team (e.g. `/follow Arsenal`)\n"
    "2\uFE0F\u20E3 Use /today to see today's matches for your teams\n"
    "3\uFE0F\u20E3 Use /reminders to turn on kickoff alerts\n\n"
    "Type /help any time to see the full command list."
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await db.upsert_user(user.id, user.username)
    await update.message.reply_text(WELCOME, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*SCP788BOT — commands*\n\n"
        "/today — Today's matches across your leagues\n"
        "/live — Live scores right now\n"
        "/follow <team> — Follow a team\n"
        "/unfollow — Stop following a team\n"
        "/myteams — View/manage your followed teams\n"
        "/standings <league> — League table\n"
        "/news <team> — Latest headlines\n"
        "/trivia — Daily sports trivia\n"
        "/reminders — Toggle kickoff alerts\n"
        "/about — About SCP788BOT"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "SCP788BOT is a free daily sports companion — live scores, fixtures, "
        "standings and news for the teams you follow. No betting, no odds, "
        "no predictions — just the facts, fast."
    )
    await update.message.reply_text(text)
