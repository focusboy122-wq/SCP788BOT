"""
SQLite persistence layer for SCP788BOT.
Stores users, their followed teams/leagues, and reminder preferences.
"""

import os
import aiosqlite

DB_PATH = os.getenv("DB_PATH", "db/scp788.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    reminders_enabled INTEGER NOT NULL DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS follows (
    user_id INTEGER NOT NULL,
    team_id TEXT NOT NULL,
    team_name TEXT NOT NULL,
    league_id TEXT,
    league_name TEXT,
    sport TEXT,
    PRIMARY KEY (user_id, team_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX IF NOT EXISTS idx_follows_user ON follows(user_id);
"""


async def init_db():
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA)
        await db.commit()


async def upsert_user(user_id: int, username: str | None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO users (user_id, username) VALUES (?, ?)
               ON CONFLICT(user_id) DO UPDATE SET username=excluded.username""",
            (user_id, username),
        )
        await db.commit()


async def add_follow(user_id: int, team_id: str, team_name: str,
                      league_id: str | None, league_name: str | None, sport: str | None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT OR IGNORE INTO follows
               (user_id, team_id, team_name, league_id, league_name, sport)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, team_id, team_name, league_id, league_name, sport),
        )
        await db.commit()


async def remove_follow(user_id: int, team_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM follows WHERE user_id = ? AND team_id = ?",
            (user_id, team_id),
        )
        await db.commit()


async def get_follows(user_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM follows WHERE user_id = ? ORDER BY team_name",
            (user_id,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def set_reminders(user_id: int, enabled: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET reminders_enabled = ? WHERE user_id = ?",
            (1 if enabled else 0, user_id),
        )
        await db.commit()


async def get_reminder_users() -> list[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT user_id FROM users WHERE reminders_enabled = 1"
        )
        rows = await cursor.fetchall()
        return [r[0] for r in rows]


async def get_all_followed_team_ids() -> list[str]:
    """Distinct team_ids anyone follows — used by the reminder scheduler
    so we only poll fixtures for teams people actually care about."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT DISTINCT team_id FROM follows")
        rows = await cursor.fetchall()
        return [r[0] for r in rows]
