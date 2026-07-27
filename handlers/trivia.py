import datetime as dt

from telegram import Update
from telegram.ext import ContextTypes

# Static question bank — rotates daily by date so everyone gets the same
# "daily challenge" feel without needing a trivia API.
QUESTIONS = [
    ("Which country has won the most FIFA World Cups?", "Brazil (5 titles)"),
    ("Which NBA team has won the most championships?", "Boston Celtics (18 titles)"),
    ("How many players are on a rugby union team on the field?", "15"),
    ("Which country hosts the Wimbledon tennis championships?", "England (UK)"),
    ("What is the maximum score in a single frame of ten-pin bowling?", "300 (a perfect game)"),
    ("Which cyclist has won the most Tour de France titles?", "Tied at 5: Anquetil, Merckx, Hinault, Indurain"),
    ("In football, how long is a standard match (excluding stoppage time)?", "90 minutes"),
    ("Which country invented the sport of cricket?", "England"),
    ("How many rings are on the Olympic flag?", "5"),
    ("Which boxer was known as 'The Greatest'?", "Muhammad Ali"),
]


async def trivia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    day_index = dt.date.today().toordinal() % len(QUESTIONS)
    question, _ = QUESTIONS[day_index]

    context.chat_data["trivia_answer"] = QUESTIONS[day_index][1]

    await update.message.reply_text(
        f"\U0001F3C5 *Daily Trivia*\n\n{question}\n\nReply with /trivia_answer to reveal the answer.",
        parse_mode="Markdown",
    )


async def trivia_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = context.chat_data.get("trivia_answer")
    if not answer:
        await update.message.reply_text("Use /trivia first to get today's question!")
        return
    await update.message.reply_text(f"\u2705 Answer: {answer}")
