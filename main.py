import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message
from aiogram.filters import Command

from settings import settings
from settings_manager import (
    toggle_user_setting,
    format_settings,
    load_settings,
    get_user_settings
)
from score_checker import check_conditions
from api_client import fetch_live_scores

# Logging: hanya log info user
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("user.log"),
        logging.StreamHandler()
    ]
)

bot = Bot(
    token=settings.bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("✅ Bot aktif. Tunggu notifikasi live skor...")
    logging.info(
        f"[START] ChatID: {message.chat.id} | Username: @{message.from_user.username} | "
        f"Name: {message.from_user.full_name} | ID: {message.from_user.id}"
    )

@dp.message(Command("settings"))
async def settings_handler(message: Message):
    config_text = format_settings(message.chat.id)
    await message.answer(f"🔧 Pengaturan Notifikasi:\n{config_text}")

@dp.message(Command("toggle_5goal"))
async def toggle_5goal_handler(message: Message):
    status = toggle_user_setting(message.chat.id, "notif_5goal")
    await message.answer(f"✅ Notifikasi 5 gol: {'ON' if status else 'OFF'}")

@dp.message(Command("toggle_4goal_half1"))
async def toggle_4goal_half1_handler(message: Message):
    status = toggle_user_setting(message.chat.id, "notif_4goal_half1")
    await message.answer(f"✅ 4 gol babak 1: {'ON' if status else 'OFF'}")

@dp.message(Command("toggle_00_60min"))
async def toggle_00_60min_handler(message: Message):
    status = toggle_user_setting(message.chat.id, "notif_00_60min")
    await message.answer(f"✅ 0-0 di menit 60: {'ON' if status else 'OFF'}")

@dp.message(Command("toggle_diff3"))
async def toggle_diff3_handler(message: Message):
    status = toggle_user_setting(message.chat.id, "notif_diff3")
    await message.answer(f"✅ Selisih 3 gol: {'ON' if status else 'OFF'}")

@dp.message(Command("toggle_3_1"))
async def toggle_3_1_handler(message: Message):
    status = toggle_user_setting(message.chat.id, "notif_3_1")
    await message.answer(f"✅ Skor 3-1/1-3: {'ON' if status else 'OFF'}")

# Loop polling live score
notified = set()

from datetime import datetime, date, timedelta
from api_client import fetch_live_scores, fetch_tomorrow_fixtures

# Tambahan state global
notified_empty_today = False
notified_schedule_tomorrow = False
last_notified_day = None

async def polling_loop():
    global notified_empty_today, notified_schedule_tomorrow, last_notified_day
    logging.info("[LOOP] Start polling loop")

    while True:
        try:
            today = date.today().isoformat()

            if today != last_notified_day:
                last_notified_day = today
                notified_empty_today = False
                notified_schedule_tomorrow = False
                logging.info("[LOOP] Hari baru, reset notifikasi")

            # Cek pertandingan hari ini
            logging.info("[LOOP] Fetching live scores...")
            matches = fetch_live_scores()
            logging.info(f"[LOOP] Fetched {len(matches)} pertandingan hari ini")

            user_settings_dict = load_settings()

            if not matches and not notified_empty_today:
                for chat_id_str in user_settings_dict:
                    await bot.send_message(int(chat_id_str), "📭 Tidak ada pertandingan hari ini.")
                notified_empty_today = True
                await asyncio.sleep(300)
                continue

            # Kirim jadwal besok
            if not notified_schedule_tomorrow:
                logging.info("[LOOP] Fetching tomorrow's fixtures...")
                tomorrow_str, tomorrow_matches = fetch_tomorrow_fixtures()
                logging.info(f"[LOOP] Dapat {len(tomorrow_matches)} jadwal besok ({tomorrow_str})")

                if tomorrow_matches:
                    msg = f"📅 Jadwal pertandingan besok:\n"
                    for m in tomorrow_matches:
                        time_str = m["starting_at"].split(" ")[1][:5]
                        msg += f"🕑 {time_str} {m['name']} ({m['league']['name']})\n"
                    for chat_id_str in user_settings_dict:
                        await bot.send_message(int(chat_id_str), msg)
                notified_schedule_tomorrow = True

            # Kirim notifikasi kondisi pertandingan
            for match in matches:
                match_id = match['id']
                for chat_id_str, user_config in user_settings_dict.items():
                    chat_id = int(chat_id_str)
                    notifs = check_conditions(match, user_config)
                    for text in notifs:
                        key = f"{chat_id}-{match_id}-{text}"
                        if key in notified:
                            continue
                        await bot.send_message(chat_id, text)
                        notified.add(key)

        except Exception as e:
            import traceback
            logging.error(f"Polling error: {e}")
            traceback.print_exc()

        await asyncio.sleep(10)
        logging.info("[LOOP] Sleep selesai, lanjut loop berikutnya")


# Main
async def main():
    asyncio.create_task(polling_loop())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
