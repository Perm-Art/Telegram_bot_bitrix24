# test_bot.py
from telegram_bot.bot import TelegramBot
from config.settings import settings

bot = TelegramBot(settings.get('telegram', 'token'))
bot.run()