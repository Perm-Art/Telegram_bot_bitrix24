"""Bitrix24 Assistant Bot - Main Entry Point"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
import openai

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Конфигурация из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
YANDEX_API_KEY = os.getenv('YANDEX_API_KEY')
YANDEX_FOLDER_ID = os.getenv('YANDEX_FOLDER_ID')
YANDEX_MODEL = os.getenv('YANDEX_MODEL', 'yandexgpt-5.1/latest')

# Инициализация Yandex GPT (только если есть ключи)
client = None
if YANDEX_API_KEY and YANDEX_FOLDER_ID:
    client = openai.OpenAI(
        api_key=YANDEX_API_KEY,
        base_url="https://ai.api.cloud.yandex.net/v1",
        project=YANDEX_FOLDER_ID
    )

SYSTEM_PROMPT = """
Вы - эксперт по API Bitrix24, помогающий разработчикам. 
Отвечайте на вопросы о методах, параметрах и примерах использования REST API.
"""

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    user = update.effective_user
    welcome_text = (
        f"👋 Здравствуйте, {user.first_name}!\n\n"
        "Я бот-помощник по API Bitrix24.\n"
        "Задайте мне вопрос о методах, параметрах или примерах использования."
    )
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщений"""
    user_text = update.message.text
    
    if client:
        try:
            response = client.responses.create(
                model=f"gpt://{YANDEX_FOLDER_ID}/{YANDEX_MODEL}",
                temperature=0.3,
                instructions=SYSTEM_PROMPT,
                input=user_text,
                max_output_tokens=2000
            )
            answer = response.output_text
            await update.message.reply_text(answer, parse_mode=ParseMode.HTML)
        except Exception as e:
            await update.message.reply_text(f"Ошибка: {str(e)}")
    else:
        await update.message.reply_text("Yandex GPT не настроен. Проверьте .env файл.")

async def main():
    """Основная функция"""
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN не найден в .env")
        return
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    print("✅ Бот запущен!")
    
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        await application.stop()

if __name__ == "__main__":
    asyncio.run(main())
