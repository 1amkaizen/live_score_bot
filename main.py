import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message
from aiogram.filters import Command
from datetime import date, timedelta

from settings import settings
from score_checker import check_conditions
from api_client import fetch_live_scores, fetch_tomorrow_fixtures

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

# Loop polling live score
notified = set()

# Tambahan state global
notified_empty_today = False
notified_schedule_tomorrow = False
last_notified_day = None

# Default user config untuk check_conditions
default_user_config = {
    "notif_5goal": True,
    "notif_4goal_half1": True,
    "notif_00_60min": True,
    "notif_diff3": True,
    "notif_3_1": True
}

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

            logging.info("[LOOP] Fetching live scores...")
            matches = fetch_live_scores()
            logging.info(f"[LOOP] Fetched {len(matches)} pertandingan hari ini")

            chat_ids = settings.chat_id_list

            if not matches and not notified_empty_today:
                for chat_id in chat_ids:
                    await bot.send_message(chat_id, "📭 Tidak ada pertandingan hari ini.")
                notified_empty_today = True
                await asyncio.sleep(300)
                continue

            if not notified_schedule_tomorrow:
                logging.info("[LOOP] Fetching tomorrow's fixtures...")
                tomorrow_str, tomorrow_matches = fetch_tomorrow_fixtures()
                logging.info(f"[LOOP] Dapat {len(tomorrow_matches)} jadwal besok ({tomorrow_str})")

                if tomorrow_matches:
                    msg = f"📅 Jadwal pertandingan besok:\n"
                    for m in tomorrow_matches:
                        time_str = m["starting_at"].split(" ")[1][:5]
                        msg += f"🕑 {time_str} {m['name']} ({m['league']['name']})\n"
                    for chat_id in chat_ids:
                        await bot.send_message(chat_id, msg)
                notified_schedule_tomorrow = True

            for match in matches:
                match_id = match['id']
                for chat_id in chat_ids:
                    # Panggil dengan user_config
                    notifs = check_conditions(match, default_user_config)
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
