import asyncio
import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Получение токена из .env
TOKEN = os.getenv('TELEGRAM_TOKEN')

if not TOKEN:
    print("❌ TELEGRAM_TOKEN не найден в .env файле!")
    print("Добавьте TELEGRAM_TOKEN=your_token в .env")
    exit(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    user = update.effective_user
    logger.info(f"Получена команда /start от {user.id}")
    await update.message.reply_text(
        f"Привет, {user.first_name}! Я работаю! 🎉"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Эхо-ответ на любое сообщение"""
    user_text = update.message.text
    user = update.effective_user
    logger.info(f"Получено сообщение от {user.id}: {user_text}")
    await update.message.reply_text(f"Вы написали: {user_text}")

async def main():
    """Основная функция"""
    print("🚀 Запуск тестового бота...")
    print(f"Токен: {TOKEN[:10]}...")
    
    # Создание приложения
    application = Application.builder().token(TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Запуск
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    print("✅ Бот запущен! Отправьте сообщение в Telegram")
    print("Нажмите Ctrl+C для остановки")
    
    # Ожидание
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\n🛑 Остановка...")
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
