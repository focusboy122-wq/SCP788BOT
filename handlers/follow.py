from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from db import database as db
from services import sportsdb


async def follow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /follow <team name>\nExample: /follow Arsenal")
        return

    query = " ".join(context.args)
    teams = await sportsdb.search_team(query)

    if not teams:
        await update.message.reply_text(
            f"Couldn't find a team matching \"{query}\". Try the full club name, e.g. \"Manchester United\"."
        )
        return

    # If we get multiple matches, let the user pick to avoid following the wrong club
    buttons = []
    for t in teams[:5]:
        label = f"{t.get('strTeam')} ({t.get('strLeague') or t.get('strSport')})"
        buttons.append([InlineKeyboardButton(label, callback_data=f"followteam:{t.get('idTeam')}")])

    context.chat_data[f"teamcache"] = {t.get("idTeam"): t for t in teams[:5]}

    await update.message.reply_text(
        "Found a few matches — tap the right one:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def follow_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    team_id = query.data.split(":", 1)[1]
    cache = context.chat_data.get("teamcache", {})
    team = cache.get(team_id)

    if not team:
        await query.edit_message_text("That selection expired — try /follow again.")
        return

    user = update.effective_user
    await db.upsert_user(user.id, user.username)
    await db.add_follow(
        user_id=user.id,
        team_id=team_id,
        team_name=team.get("strTeam"),
        league_id=team.get("idLeague"),
        league_name=team.get("strLeague"),
        sport=team.get("strSport"),
    )

    await query.edit_message_text(f"\u2705 You're now following {team.get('strTeam')}!")


async def unfollow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    follows = await db.get_follows(user.id)

    if not follows:
        await update.message.reply_text("You're not following any teams yet — try /follow <team name>.")
        return

    buttons = [
        [InlineKeyboardButton(f["team_name"], callback_data=f"unfollowteam:{f['team_id']}")]
        for f in follows
    ]
    await update.message.reply_text(
        "Tap a team to unfollow:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def unfollow_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    team_id = query.data.split(":", 1)[1]
    user = update.effective_user
    await db.remove_follow(user.id, team_id)
    await query.edit_message_text("Unfollowed. Use /myteams to see who's left.")


async def myteams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    follows = await db.get_follows(user.id)

    if not follows:
        await update.message.reply_text("You're not following any teams yet — try /follow <team name>.")
        return

    lines = ["*Your teams:*"]
    for f in follows:
        lines.append(f"\u2022 {f['team_name']} ({f['league_name'] or f['sport']})")
    lines.append("\nUse /unfollow to remove one.")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
