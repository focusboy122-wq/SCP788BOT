"""
Thin async wrapper around TheSportsDB's free-tier API.
Docs: https://www.thesportsdb.com/free_sport_api
Free test key "3" works with no signup; set THESPORTSDB_KEY to your own
patreon key later if you want higher rate limits.
"""

import os
import datetime as dt
import aiohttp

KEY = os.getenv("THESPORTSDB_KEY", "3")
BASE = f"https://www.thesportsdb.com/api/v1/json/{KEY}"


async def _get(session: aiohttp.ClientSession, path: str, params: dict | None = None):
    async with session.get(f"{BASE}/{path}", params=params, timeout=15) as resp:
        if resp.status != 200:
            return None
        return await resp.json()


async def search_team(team_name: str) -> list[dict]:
    async with aiohttp.ClientSession() as session:
        data = await _get(session, "searchteams.php", {"t": team_name})
        if not data or not data.get("teams"):
            return []
        return data["teams"]


async def team_next_events(team_id: str) -> list[dict]:
    async with aiohttp.ClientSession() as session:
        data = await _get(session, "eventsnext.php", {"id": team_id})
        if not data or not data.get("events"):
            return []
        return data["events"]


async def team_last_events(team_id: str, limit: int = 5) -> list[dict]:
    async with aiohttp.ClientSession() as session:
        data = await _get(session, "eventslast.php", {"id": team_id})
        if not data or not data.get("results"):
            return []
        return data["results"][:limit]


async def events_on_date(date: dt.date, league_id: str | None = None) -> list[dict]:
    params = {"d": date.isoformat()}
    if league_id:
        params["l"] = league_id
    async with aiohttp.ClientSession() as session:
        data = await _get(session, "eventsday.php", params)
        if not data or not data.get("events"):
            return []
        return data["events"]


async def all_leagues() -> list[dict]:
    async with aiohttp.ClientSession() as session:
        data = await _get(session, "all_leagues.php")
        if not data or not data.get("leagues"):
            return []
        return data["leagues"]


async def find_league_by_name(name: str) -> dict | None:
    """Case-insensitive substring match against all_leagues.php,
    since TheSportsDB's free tier has no direct league search endpoint."""
    leagues = await all_leagues()
    name_l = name.lower()
    for lg in leagues:
        if name_l in (lg.get("strLeague") or "").lower():
            return lg
    return None


def current_season_guess() -> str:
    """Most European leagues use e.g. '2025-2026' season strings."""
    import datetime as _dt
    today = _dt.date.today()
    if today.month >= 7:
        return f"{today.year}-{today.year + 1}"
    return f"{today.year - 1}-{today.year}"


async def league_table(league_id: str, season: str) -> list[dict]:
    async with aiohttp.ClientSession() as session:
        data = await _get(session, "lookuptable.php", {"l": league_id, "s": season})
        if not data or not data.get("table"):
            return []
        return data["table"]


async def live_scores_for_teams(team_ids: set[str]) -> list[dict]:
    """
    TheSportsDB's free tier has no single 'all live scores' endpoint,
    so we check each followed team's next/last event and keep the ones
    whose strStatus indicates in-progress play.
    """
    live = []
    async with aiohttp.ClientSession() as session:
        for tid in team_ids:
            data = await _get(session, "eventsnext.php", {"id": tid})
            if not data or not data.get("events"):
                continue
            for ev in data["events"]:
                status = (ev.get("strStatus") or "").lower()
                if status and status not in ("not started", "ns", ""):
                    live.append(ev)
    return live
