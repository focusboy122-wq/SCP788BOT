from telegram import Update
from telegram.ext import ContextTypes

from db import database as db
from services import news as news_service


async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    query = " ".join(context.args) if context.args else None

    if not query:
        follows = await db.get_follows(user.id)
        if follows:
            query = follows[0]["team_name"]

    headlines = news_service.get_headlines(query)

    if not headlines:
        await update.message.reply_text("No headlines found right now — try again shortly.")
        return

    title = f"for {query}" if query else "— top sports headlines"
    lines = [f"\U0001F4F0 *Latest news {title}*\n"]
    for h in headlines:
        lines.append(f"\u2022 [{h['title']}]({h['link']})")

    await update.message.reply_text(
        "\n".join(lines), parse_mode="Markdown", disable_web_page_preview=True
    )
