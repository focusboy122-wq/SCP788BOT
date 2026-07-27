import datetime as dt

from telegram import Update
from telegram.ext import ContextTypes

from db import database as db
from services import sportsdb


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    follows = await db.get_follows(user.id)

    if not follows:
        await update.message.reply_text(
            "You're not following any teams yet — try /follow <team name> first."
        )
        return

    await update.message.reply_text("Checking today's fixtures for your teams...")

    today_date = dt.date.today()
    lines = [f"\U0001F4C5 *Today's matches* ({today_date.isoformat()})\n"]
    found_any = False

    for f in follows:
        events = await sportsdb.team_next_events(f["team_id"])
        todays = [e for e in events if (e.get("dateEvent") == today_date.isoformat())]
        for ev in todays:
            found_any = True
            home = ev.get("strHomeTeam", "?")
            away = ev.get("strAwayTeam", "?")
            time_str = ev.get("strTime", "TBD")
            lines.append(f"\u2022 {home} vs {away} — {time_str} UTC ({f['team_name']})")

    if not found_any:
        lines.append("No matches today for your followed teams. Check /myteams or try /follow to add more.")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
