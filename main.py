import os
import logging

from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
)

from db.database import init_db
from handlers import start as start_h
from handlers import follow as follow_h
from handlers import today as today_h
from handlers import live as live_h
from handlers import standings as standings_h
from handlers import news as news_h
from handlers import trivia as trivia_h
from handlers import reminders as reminders_h
from services.scheduler import check_and_send_reminders

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def _post_init(app: Application):
    await init_db()
    logger.info("Database ready.")

    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_and_send_reminders, "interval", minutes=5, args=[app])
    scheduler.start()
    logger.info("Reminder scheduler started (every 5 min).")


def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN not set — copy .env.example to .env and fill it in.")

    app = Application.builder().token(token).post_init(_post_init).build()

    # Core commands
    app.add_handler(CommandHandler("start", start_h.start))
    app.add_handler(CommandHandler("help", start_h.help_command))
    app.add_handler(CommandHandler("about", start_h.about))

    # Follow / unfollow / myteams
    app.add_handler(CommandHandler("follow", follow_h.follow))
    app.add_handler(CommandHandler("unfollow", follow_h.unfollow))
    app.add_handler(CommandHandler("myteams", follow_h.myteams))
    app.add_handler(CallbackQueryHandler(follow_h.follow_callback, pattern=r"^followteam:"))
    app.add_handler(CallbackQueryHandler(follow_h.unfollow_callback, pattern=r"^unfollowteam:"))

    # Scores / fixtures / standings / news
    app.add_handler(CommandHandler("today", today_h.today))
    app.add_handler(CommandHandler("live", live_h.live))
    app.add_handler(CommandHandler("standings", standings_h.standings))
    app.add_handler(CommandHandler("news", news_h.news))

    # Trivia
    app.add_handler(CommandHandler("trivia", trivia_h.trivia))
    app.add_handler(CommandHandler("trivia_answer", trivia_h.trivia_answer))

    # Reminders
    app.add_handler(CommandHandler("reminders", reminders_h.reminders))

    logger.info("SCP788BOT starting (polling mode)...")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
