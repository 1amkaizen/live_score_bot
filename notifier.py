from aiogram import Bot
from settings import settings
from aiogram import Bot
from settings import settings

bot = Bot(token=settings.bot_token)

async def send_message(text: str):
    await bot.send_message(chat_id=settings.chat_id, text=text)
