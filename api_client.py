import requests
from datetime import datetime
from settings import settings
from datetime import date, timedelta

def fetch_live_scores():
    today = datetime.utcnow().strftime('%Y-%m-%d')
    url = f"https://api.sportmonks.com/v3/football/fixtures/date/{today}"
    params = {
        "api_token": settings.api_key,
        "include": "scores"
    }

    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()
        matches = data.get("data", [])
        print(f"[INFO] Ditemukan {len(matches)} pertandingan dari SportMonks untuk tanggal {today}")
        return matches
    except Exception as e:
        print(f"[ERROR] Gagal fetch dari SportMonks: {e}")
        return []

def fetch_tomorrow_fixtures():
    tomorrow = date.today() + timedelta(days=1)
    url = f"https://api.sportmonks.com/v3/football/fixtures/date/{tomorrow.isoformat()}"
    params = {
        "api_token": settings.api_key,
        "include": "league"
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    matches = data.get("data", [])
    return tomorrow.isoformat(), matches
