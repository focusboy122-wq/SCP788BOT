from telegram import Update
from telegram.ext import ContextTypes

from db import database as db
from services import sportsdb


async def standings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    league_id = None
    league_name = None

    if context.args:
        query = " ".join(context.args)
        league = await sportsdb.find_league_by_name(query)
        if not league:
            await update.message.reply_text(
                f"Couldn't find a league matching \"{query}\". Try e.g. \"Premier League\"."
            )
            return
        league_id = league.get("idLeague")
        league_name = league.get("strLeague")
    else:
        follows = await db.get_follows(user.id)
        if not follows or not follows[0].get("league_id"):
            await update.message.reply_text(
                "Usage: /standings <league name>\nOr follow a team first with /follow so I know which league to show."
            )
            return
        league_id = follows[0]["league_id"]
        league_name = follows[0]["league_name"]

    season = sportsdb.current_season_guess()
    table = await sportsdb.league_table(league_id, season)

    if not table:
        await update.message.reply_text(
            f"No standings available for {league_name} right now (season may not have started)."
        )
        return

    lines = [f"\U0001F4CA *{league_name} — {season}*\n"]
    for row in table[:20]:
        pos = row.get("intRank", "?")
        team = row.get("strTeam", "?")
        pts = row.get("intPoints", "?")
        played = row.get("intPlayed", "?")
        lines.append(f"{pos}. {team} — {pts} pts ({played} pl)")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
