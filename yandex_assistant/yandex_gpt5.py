import openai
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class YandexGPT5:
    """Класс для работы с Yandex GPT 5.1"""
    
    def __init__(self, api_key: str, folder_id: str, model: str = "yandexgpt-5.1/latest"):
        """
        Инициализация клиента Yandex GPT
        
        Args:
            api_key: API ключ Yandex Cloud
            folder_id: ID каталога Yandex Cloud
            model: Название модели
        """
        self.api_key = api_key
        self.folder_id = folder_id
        self.model = f"gpt://{folder_id}/{model}"
        
        # Создание клиента OpenAI
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://ai.api.cloud.yandex.net/v1",
            project=folder_id
        )
        
        logger.info(f"YandexGPT5 initialized with model: {self.model}")
    
    def generate_response(
        self,
        prompt: str,
        instructions: str = "",
        context: str = "",
        conversation_history: List[Dict] = None,
        temperature: float = 0.3,
        max_tokens: int = 1500
    ) -> str:
        """
        Генерация ответа с использованием Yandex GPT 5.1
        
        Args:
            prompt: Запрос пользователя
            instructions: Системные инструкции
            context: Контекст из документации
            conversation_history: История диалога
            temperature: Температура (креативность)
            max_tokens: Максимальное количество токенов
            
        Returns:
            Строка с ответом
        """
        try:
            # Формирование системного промпта
            if not instructions:
                instructions = self._get_default_instructions()
            
            # Добавление контекста
            if context:
                instructions += f"\n\nКонтекст из документации:\n{context}"
            
            # Подготовка входных данных
            input_text = self._prepare_input(prompt, conversation_history)
            
            # Вызов API
            response = self.client.responses.create(
                model=self.model,
                temperature=temperature,
                instructions=instructions,
                input=input_text,
                max_output_tokens=max_tokens
            )
            
            # Извлечение ответа
            answer = response.output_text
            
            logger.info(f"Generated response of length: {len(answer)}")
            return answer
            
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return self._get_fallback_response(prompt)
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return self._get_fallback_response(prompt)
    
    def _get_default_instructions(self) -> str:
        """Системные инструкции по умолчанию"""
        return (
            "Вы - эксперт по API Bitrix24, помогающий разработчикам. "
            "Отвечайте на вопросы о методах, параметрах и примерах использования REST API.\n\n"
            "Правила ответов:\n"
            "1. Отвечайте кратко и по существу\n"
            "2. Приводите примеры кода, если это уместно\n"
            "3. Указывайте точные названия методов и параметров\n"
            "4. Если информации недостаточно, честно скажите об этом\n"
            "5. Используйте информацию из предоставленного контекста\n"
            "6. Форматируйте ответы для удобного чтения в Telegram\n"
            "7. Для кода используйте HTML-теги <code>"
        )
    
    def _prepare_input(
        self,
        prompt: str,
        conversation_history: List[Dict] = None
    ) -> str:
        """Подготовка входных данных с учетом истории"""
        if not conversation_history:
            return prompt
        
        # Формирование контекста из истории
        history_text = "Предыдущий диалог:\n"
        for msg in conversation_history[-5:]:  # Последние 5 сообщений
            role = "Пользователь" if msg.get('is_from_user') else "Ассистент"
            history_text += f"{role}: {msg.get('text', '')}\n"
        
        return f"{history_text}\n\nТекущий вопрос: {prompt}"
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Запасной ответ при ошибке"""
        return (
            "К сожалению, не удалось получить ответ от модели. "
            "Попробуйте переформулировать вопрос или обратитесь к документации: "
            "https://apidocs.bitrix24.ru/"
        )
    
    def test_connection(self) -> bool:
        """Проверка подключения к API"""
        try:
            response = self.generate_response(
                prompt="Проверка связи. Ответьте 'OK'",
                max_tokens=10
            )
            return len(response) > 0
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
