# settings_manager.py
import json
from pathlib import Path

SETTINGS_FILE = Path("user_settings.json")

DEFAULT_SETTINGS = {
    "notif_5goal": True,
    "notif_4goal_half1": True,
    "notif_00_60min": True,
    "notif_diff3": True,
    "notif_3_1": True
}

def load_settings():
    if not SETTINGS_FILE.exists():
        return {}
    with open(SETTINGS_FILE, 'r') as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

def get_user_settings(user_id: int):
    settings = load_settings()
    user_id_str = str(user_id)

    if user_id_str not in settings:
        settings[user_id_str] = DEFAULT_SETTINGS.copy()
        save_settings(settings)

    return settings[user_id_str]


def toggle_user_setting(user_id: int, key: str):
    settings = load_settings()
    user_id_str = str(user_id)
    user_settings = settings.get(user_id_str, DEFAULT_SETTINGS.copy())

    if key in user_settings:
        user_settings[key] = not user_settings[key]

    settings[user_id_str] = user_settings
    save_settings(settings)
    return user_settings[key]

def format_settings(user_id: int):
    s = get_user_settings(user_id)
    return "\n".join([
        f"✅ Total 5 gol: {'ON' if s['notif_5goal'] else 'OFF'}",
        f"✅ 4 gol babak 1: {'ON' if s['notif_4goal_half1'] else 'OFF'}",
        f"✅ 0-0 menit 60: {'ON' if s['notif_00_60min'] else 'OFF'}",
        f"✅ Selisih 3 gol: {'ON' if s['notif_diff3'] else 'OFF'}",
        f"✅ Skor 3-1/1-3: {'ON' if s['notif_3_1'] else 'OFF'}"
    ])
