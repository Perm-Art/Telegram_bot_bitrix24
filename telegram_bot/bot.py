import logging
from typing import Optional, Dict, Any
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)

class TelegramBot:
    """Класс Telegram бота"""
    
    def __init__(self, token: str, db_manager=None, orchestrator=None):
        """
        Инициализация Telegram бота
        
        Args:
            token: Токен Telegram бота
            db_manager: Менеджер базы данных
            orchestrator: Оркестратор для обработки запросов
        """
        self.token = token
        self.db_manager = db_manager
        self.orchestrator = orchestrator
        self.application = None
        
        logger.info("TelegramBot initialized")
    
    async def setup(self):
        """Настройка бота и регистрация обработчиков"""
        if not self.token:
            raise ValueError("Telegram token not configured")
        
        # Создание приложения
        self.application = Application.builder().token(self.token).build()
        
        # Регистрация обработчиков команд
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("new", self.new_conversation))
        self.application.add_handler(CommandHandler("history", self.show_history))
        self.application.add_handler(CommandHandler("stats", self.show_stats))
        
        # Регистрация обработчика текстовых сообщений
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_message
        ))
        
        logger.info("TelegramBot setup completed")
    
    async def start(self):
        """Запуск бота"""
        if not self.application:
            await self.setup()
        
        logger.info("Starting Telegram bot...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        logger.info("Telegram bot started")
    
    async def stop(self):
        """Остановка бота"""
        if self.application:
            logger.info("Stopping Telegram bot...")
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Telegram bot stopped")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start"""
        user = update.effective_user
        
        # Регистрация пользователя в БД
        if self.db_manager:
            user_db = self.db_manager.get_or_create_user(
                telegram_id=str(user.id),
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
        
        welcome_text = (
            f"👋 Здравствуйте, {user.first_name}!\n\n"
            "Я чат-бот для помощи разработчикам по API Bitrix24. "
            "Могу ответить на ваши вопросы о методах, параметрах и примерах использования.\n\n"
            "Просто задайте мне вопрос, и я постараюсь найти ответ в документации.\n\n"
            "📚 Доступные команды:\n"
            "/help - показать справку\n"
            "/new - начать новый диалог\n"
            "/history - показать историю сообщений\n"
            "/stats - показать статистику"
        )
        
        await update.message.reply_text(welcome_text)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /help"""
        help_text = (
            "📚 <b>Справка по использованию бота</b>\n\n"
            "Я могу помочь с вопросами по API Bitrix24:\n"
            "• Методы REST API\n"
            "• Параметры запросов\n"
            "• Примеры кода\n"
            "• Структура данных\n\n"
            "<b>Примеры вопросов:</b>\n"
            "• Как получить список сделок?\n"
            "• Какие параметры у метода user.get?\n"
            "• Как создать лид через REST API?\n"
            "• Как настроить вебхук?\n\n"
            "<b>Команды:</b>\n"
            "/new - начать новый диалог\n"
            "/history - история последних сообщений\n"
            "/stats - статистика использования"
        )
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)
    
    async def new_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало нового диалога"""
        user = update.effective_user
        
        if self.db_manager:
            # Получаем или создаем пользователя
            user_db = self.db_manager.get_or_create_user(str(user.id))
            
            # Завершаем текущий диалог
            active_conversation = self.db_manager.get_active_conversation(user_db['id'])
            if active_conversation:
                self.db_manager.end_conversation(active_conversation['id'])
            
            # Создаем новый диалог
            conversation = self.db_manager.create_conversation(user_db['id'])
        
        await update.message.reply_text(
            "🆕 Начат новый диалог. Задавайте ваш вопрос!"
        )
    
    async def show_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать историю сообщений"""
        user = update.effective_user
        
        if not self.db_manager:
            await update.message.reply_text("База данных не настроена.")
            return
        
        # Получаем пользователя
        user_db = self.db_manager.get_or_create_user(str(user.id))
        
        # Получаем активный диалог
        conversation = self.db_manager.get_active_conversation(user_db['id'])
        if not conversation:
            await update.message.reply_text("История сообщений пуста.")
            return
        
        # Получаем историю
        history = self.db_manager.get_conversation_history(conversation['id'], limit=10)
        
        if not history:
            await update.message.reply_text("История сообщений пуста.")
            return
        
        history_text = "📝 <b>Последние сообщения:</b>\n\n"
        for msg in history:
            prefix = "👤 <b>Вы:</b> " if msg['is_from_user'] else "🤖 <b>Бот:</b> "
            text = msg['text'][:100]
            if len(msg['text']) > 100:
                text += "..."
            history_text += f"{prefix}{text}\n\n"
        
        await update.message.reply_text(history_text, parse_mode=ParseMode.HTML)
    
    async def show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать статистику"""
        if not self.db_manager:
            await update.message.reply_text("База данных не настроена.")
            return
        
        stats = self.db_manager.get_statistics()
        
        stats_text = (
            "📊 <b>Статистика:</b>\n\n"
            f"👥 Пользователей: {stats.get('users', 0)}\n"
            f"💬 Диалогов: {stats.get('conversations', 0)}\n"
            f"📝 Сообщений: {stats.get('messages', 0)}\n"
            f"📚 Документов в базе знаний: {stats.get('knowledge_base', 0)}"
        )
        
        await update.message.reply_text(stats_text, parse_mode=ParseMode.HTML)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        user = update.effective_user
        user_text = update.message.text
        
        logger.info(f"Received message from {user.id}: {user_text[:50]}")
        
        # Регистрация пользователя
        user_db = None
        conversation = None
        
        if self.db_manager:
            user_db = self.db_manager.get_or_create_user(
                telegram_id=str(user.id),
                username=user.username,
                first_name=user.first_name
            )
            
            # Получение или создание активного диалога
            conversation = self.db_manager.get_active_conversation(user_db['id'])
            if not conversation:
                conversation = self.db_manager.create_conversation(user_db['id'])
            
            # Сохранение сообщения пользователя
            self.db_manager.save_message(
                conversation['id'], 
                user_text, 
                is_from_user=True
            )
        
        # Отправка индикатора набора текста
        await update.message.chat.send_action(action="typing")
        
        try:
            # Получение ответа
            if self.orchestrator:
                # Используем оркестратор для обработки
                response = await self.orchestrator.process_query(
                    query=user_text,
                    user_id=user_db['id'] if user_db else None,
                    conversation_id=conversation['id'] if conversation else None
                )
            else:
                # Временный ответ, если оркестратор не настроен
                response = self._get_temporary_response(user_text)
            
            # Сохранение ответа бота
            if self.db_manager and conversation:
                self.db_manager.save_message(
                    conversation['id'], 
                    response, 
                    is_from_user=False
                )
            
            # Отправка ответа
            await update.message.reply_text(response)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            error_text = (
                "😔 Произошла ошибка при обработке вашего запроса. "
                "Пожалуйста, попробуйте позже."
            )
            await update.message.reply_text(error_text)
    
    def _get_temporary_response(self, query: str) -> str:
        """Временный ответ, пока оркестратор не настроен"""
        # Простые заглушки для тестирования
        query_lower = query.lower()
        
        if "привет" in query_lower or "hello" in query_lower:
            return "👋 Здравствуйте! Я бот-помощник по Bitrix24 API. Задайте мне вопрос о методах, параметрах или примерах использования."
        
        elif "сделка" in query_lower or "deal" in query_lower:
            return (
                "📚 <b>Работа со сделками в Bitrix24</b>\n\n"
                "Основные методы:\n"
                "• <code>crm.deal.list</code> - получение списка сделок\n"
                "• <code>crm.deal.get</code> - получение сделки по ID\n"
                "• <code>crm.deal.add</code> - создание сделки\n"
                "• <code>crm.deal.update</code> - обновление сделки\n"
                "• <code>crm.deal.delete</code> - удаление сделки\n\n"
                "Пример получения списка:\n"
                "<code>GET /rest/crm.deal.list</code>"
            )
        
        elif "лид" in query_lower or "lead" in query_lower:
            return (
                "📚 <b>Работа с лидами в Bitrix24</b>\n\n"
                "Основные методы:\n"
                "• <code>crm.lead.list</code> - получение списка лидов\n"
                "• <code>crm.lead.add</code> - создание лида\n"
                "• <code>crm.lead.update</code> - обновление лида\n\n"
                "Пример создания лида:\n"
                "<code>POST /rest/crm.lead.add</code>"
            )
        
        elif "контакт" in query_lower or "contact" in query_lower:
            return (
                "📚 <b>Работа с контактами в Bitrix24</b>\n\n"
                "Основные методы:\n"
                "• <code>crm.contact.list</code> - получение списка контактов\n"
                "• <code>crm.contact.get</code> - получение контакта\n"
                "• <code>crm.contact.add</code> - создание контакта\n"
                "• <code>crm.contact.update</code> - обновление контакта"
            )
        
        elif "help" in query_lower or "помощ" in query_lower:
            return (
                "Я могу помочь с вопросами по API Bitrix24.\n\n"
                "Примеры вопросов:\n"
                "• Как получить список сделок?\n"
                "• Как создать лид?\n"
                "• Какие методы есть для работы с контактами?\n\n"
                "Используйте /help для получения подробной справки."
            )
        
        else:
            return (
                f"Вы спросили: <i>{query}</i>\n\n"
                "🔧 Я пока нахожусь в режиме настройки. "
                "Скоро я смогу отвечать на вопросы по API Bitrix24, "
                "используя Yandex GPT и базу знаний.\n\n"
                "Попробуйте спросить про:\n"
                "• Сделки (deals)\n"
                "• Лиды (leads)\n"
                "• Контакты (contacts)\n"
                "• Компании (companies)"
            )
