from telegram import Update
from telegram.ext import ContextTypes

from db import database as db
from services import sportsdb


async def live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    follows = await db.get_follows(user.id)

    if not follows:
        await update.message.reply_text(
            "You're not following any teams yet — try /follow <team name> first."
        )
        return

    await update.message.reply_text("Checking for live matches...")

    team_ids = {f["team_id"] for f in follows}
    id_to_name = {f["team_id"]: f["team_name"] for f in follows}
    live_events = await sportsdb.live_scores_for_teams(team_ids)

    if not live_events:
        await update.message.reply_text(
            "Nothing live right now for your teams. Try /today to see upcoming fixtures."
        )
        return

    lines = ["\U0001F534 *Live now:*\n"]
    for ev in live_events:
        home = ev.get("strHomeTeam", "?")
        away = ev.get("strAwayTeam", "?")
        score = f"{ev.get('intHomeScore', '-')}-{ev.get('intAwayScore', '-')}"
        status = ev.get("strStatus", "")
        lines.append(f"\u2022 {home} {score} {away} ({status})")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
