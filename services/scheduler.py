"""
Polls upcoming fixtures for followed teams and DMs users ~30 minutes
before kickoff, for anyone who has /reminders on.

Runs as an APScheduler job inside the same process as the bot — no
separate worker needed, which keeps this simple to deploy on Railway.
"""

import datetime as dt
import logging

from telegram.ext import Application
from telegram.error import Forbidden

from db import database as db
from services import sportsdb

logger = logging.getLogger(__name__)

# Tracks event_ids we've already reminded about this run, so we don't
# spam the same fixture twice (resets on process restart, which is fine
# for a ~30 min reminder window).
_already_sent: set[str] = set()


async def check_and_send_reminders(app: Application):
    reminder_user_ids = await db.get_reminder_users()
    if not reminder_user_ids:
        return

    now = dt.datetime.utcnow()
    window_end = now + dt.timedelta(minutes=35)

    for user_id in reminder_user_ids:
        follows = await db.get_follows(user_id)
        for f in follows:
            events = await sportsdb.team_next_events(f["team_id"])
            for ev in events:
                event_id = ev.get("idEvent")
                date_str = ev.get("dateEvent")
                time_str = ev.get("strTime")
                if not date_str or not time_str or not event_id:
                    continue
                if f"{user_id}:{event_id}" in _already_sent:
                    continue

                try:
                    kickoff = dt.datetime.fromisoformat(f"{date_str}T{time_str}")
                except ValueError:
                    continue

                if now <= kickoff <= window_end:
                    home = ev.get("strHomeTeam", "?")
                    away = ev.get("strAwayTeam", "?")
                    text = (
                        f"\u23F0 Kickoff soon: {home} vs {away} "
                        f"at {time_str} UTC ({f['team_name']})"
                    )
                    try:
                        await app.bot.send_message(chat_id=user_id, text=text)
                        _already_sent.add(f"{user_id}:{event_id}")
                    except Forbidden:
                        # User blocked the bot — nothing to do
                        logger.info("User %s blocked the bot, skipping reminder", user_id)
