import logging
from typing import Optional, Dict, Any, List
from config.settings import settings
from database.db_manager import DatabaseManager
from yandex_assistant.yandex_gpt5 import YandexGPT5

logger = logging.getLogger(__name__)

class Orchestrator:
    """Оркестратор для обработки запросов"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Инициализация оркестратора
        
        Args:
            db_manager: Менеджер базы данных
        """
        self.db_manager = db_manager
        
        # Инициализация Yandex GPT
        self.yandex_gpt = YandexGPT5(
            api_key=settings.get('yandex', 'api_key'),
            folder_id=settings.get('yandex', 'folder_id'),
            model=settings.get('yandex', 'model', 'yandexgpt-5.1/latest')
        )
        
        # Системный промпт для Bitrix24
        self.system_prompt = """
        Вы - эксперт по API Bitrix24. Ваша задача - помогать разработчикам 
        с вопросами о REST API, методах, параметрах и примерах использования.
        
        Основные темы:
        - REST API методы
        - Вебхуки
        - OAuth 2.0 авторизация
        - Работа с сущностями (лиды, сделки, контакты, компании)
        - Пользовательские поля
        - События и подписки
        
        Отвечайте точно и по делу, приводите примеры кода когда это уместно.
        """
        
        logger.info("Orchestrator initialized")
    
    async def process_query(
        self,
        query: str,
        user_id: Optional[int] = None,
        conversation_id: Optional[int] = None
    ) -> str:
        """
        Обработка запроса пользователя
        
        Args:
            query: Запрос пользователя
            user_id: ID пользователя
            conversation_id: ID диалога
            
        Returns:
            Ответ на запрос
        """
        try:
            logger.info(f"Processing query: {query[:50]}")
            
            # 1. Поиск в базе знаний
            context = ""
            if self.db_manager:
                knowledge_results = self.db_manager.search_knowledge(query, limit=5)
                
                if knowledge_results:
                    context = self._format_context(knowledge_results)
                    logger.info(f"Found {len(knowledge_results)} relevant documents")
                else:
                    logger.info("No relevant documents found in knowledge base")
            
            # 2. Получение истории диалога
            history = []
            if self.db_manager and conversation_id:
                history = self.db_manager.get_conversation_history(
                    conversation_id,
                    limit=10
                )
                
                # Форматирование истории
                history = [
                    {
                        "text": msg.get('text', ''),
                        "is_from_user": msg.get('is_from_user', True)
                    }
                    for msg in history
                ]
            
            # 3. Генерация ответа
            response = self.yandex_gpt.generate_response(
                prompt=query,
                instructions=self.system_prompt,
                context=context,
                conversation_history=history,
                temperature=0.3,
                max_tokens=1500
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in process_query: {e}", exc_info=True)
            return (
                "Произошла ошибка при обработке запроса. "
                "Пожалуйста, попробуйте еще раз или переформулируйте вопрос."
            )
    
    def _format_context(self, knowledge_results: List[Dict]) -> str:
        """Форматирование контекста из базы знаний"""
        context_parts = []
        
        for item in knowledge_results[:3]:  # Берем только 3 наиболее релевантных
            context_parts.append(f"""
### {item.get('title', 'Без заголовка')}
Категория: {item.get('category', 'general')}
{item.get('content', '')[:1000]}
Источник: {item.get('url', '')}
""")
        
        return "\n\n".join(context_parts)
    
    async def test_yandex_connection(self) -> bool:
        """Проверка подключения к Yandex GPT"""
        return self.yandex_gpt.test_connection()
