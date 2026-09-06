# Создайте файл db_manager.py

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Менеджер для работы с базой данных"""
    
    def __init__(self):
        """Инициализация менеджера базы данных"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("DatabaseManager initialized (stub mode)")
        
        # Временное хранилище в памяти
        self._users = {}
        self._conversations = {}
        self._messages = {}
        self._knowledge_base = {}
        
        # Счетчики для ID
        self._user_counter = 0
        self._conversation_counter = 0
        self._message_counter = 0
        self._knowledge_counter = 0
    
    # Методы для работы с пользователями
    
    def get_or_create_user(self, telegram_id: str, username: str = None,
                          first_name: str = None, last_name: str = None) -> Dict:
        """Получение или создание пользователя"""
        # Ищем пользователя по telegram_id
        for user_id, user in self._users.items():
            if user.get('telegram_id') == telegram_id:
                return user
        
        # Создаем нового пользователя
        self._user_counter += 1
        user = {
            'id': self._user_counter,
            'telegram_id': telegram_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'is_active': True
        }
        
        self._users[self._user_counter] = user
        self.logger.info(f"Created new user: {telegram_id}")
        return user
    
    def update_user_activity(self, telegram_id: str):
        """Обновление активности пользователя"""
        for user in self._users.values():
            if user.get('telegram_id') == telegram_id:
                user['last_activity'] = datetime.now()
                break
    
    def get_user(self, telegram_id: str) -> Optional[Dict]:
        """Получение пользователя по telegram_id"""
        for user in self._users.values():
            if user.get('telegram_id') == telegram_id:
                return user
        return None
    
    # Методы для работы с диалогами
    
    def create_conversation(self, user_id: int) -> Dict:
        """Создание нового диалога"""
        self._conversation_counter += 1
        conversation = {
            'id': self._conversation_counter,
            'user_id': user_id,
            'started_at': datetime.now(),
            'ended_at': None,
            'context_data': {}
        }
        
        self._conversations[self._conversation_counter] = conversation
        self.logger.info(f"Created conversation {self._conversation_counter} for user {user_id}")
        return conversation
    
    def get_active_conversation(self, user_id: int) -> Optional[Dict]:
        """Получение активного диалога пользователя"""
        for conversation in self._conversations.values():
            if conversation.get('user_id') == user_id and conversation.get('ended_at') is None:
                return conversation
        return None
    
    def end_conversation(self, conversation_id: int):
        """Завершение диалога"""
        if conversation_id in self._conversations:
            self._conversations[conversation_id]['ended_at'] = datetime.now()
            self.logger.info(f"Ended conversation {conversation_id}")
    
    # Методы для работы с сообщениями
    
    def save_message(self, conversation_id: int, text: str, is_from_user: bool) -> Dict:
        """Сохранение сообщения"""
        self._message_counter += 1
        message = {
            'id': self._message_counter,
            'conversation_id': conversation_id,
            'text': text,
            'is_from_user': is_from_user,
            'created_at': datetime.now(),
            'metadata': {}
        }
        
        self._messages[self._message_counter] = message
        
        # Сохраняем в историю диалога
        if conversation_id in self._conversations:
            if 'messages' not in self._conversations[conversation_id]:
                self._conversations[conversation_id]['messages'] = []
            self._conversations[conversation_id]['messages'].append(message)
        
        return message
    
    def get_conversation_history(self, conversation_id: int, limit: int = 10) -> List[Dict]:
        """Получение истории диалога"""
        if conversation_id in self._conversations:
            messages = self._conversations[conversation_id].get('messages', [])
            return messages[-limit:] if limit > 0 else messages
        return []
    
    # Методы для работы с базой знаний
    
    def save_knowledge(self, url: str, title: str, content: str, category: str = "general"):
        """Сохранение записи в базу знаний"""
        # Проверяем, существует ли запись с таким URL
        for knowledge_id, knowledge in self._knowledge_base.items():
            if knowledge.get('url') == url:
                # Обновляем существующую запись
                knowledge['title'] = title
                knowledge['content'] = content
                knowledge['category'] = category
                knowledge['updated_at'] = datetime.now()
                self.logger.info(f"Updated knowledge: {title}")
                return
        
        # Создаем новую запись
        self._knowledge_counter += 1
        knowledge = {
            'id': self._knowledge_counter,
            'url': url,
            'title': title,
            'content': content,
            'category': category,
            'tags': '',
            'updated_at': datetime.now()
        }
        
        self._knowledge_base[self._knowledge_counter] = knowledge
        self.logger.info(f"Added knowledge: {title}")
    
    def search_knowledge(self, query: str, limit: int = 5) -> List[Dict]:
        """Поиск в базе знаний"""
        results = []
        query_lower = query.lower()
        
        for knowledge in self._knowledge_base.values():
            # Простой поиск по совпадению
            if (query_lower in knowledge.get('title', '').lower() or
                query_lower in knowledge.get('content', '').lower() or
                query_lower in knowledge.get('category', '').lower()):
                results.append(knowledge)
                
                if len(results) >= limit:
                    break
        
        return results
    
    def get_all_knowledge(self) -> List[Dict]:
        """Получение всей базы знаний"""
        return list(self._knowledge_base.values())
    
    def clear_knowledge_base(self):
        """Очистка базы знаний"""
        self._knowledge_base.clear()
        self._knowledge_counter = 0
        self.logger.info("Knowledge base cleared")
    
    # Методы для статистики
    
    def get_statistics(self) -> Dict:
        """Получение статистики"""
        return {
            'users': len(self._users),
            'conversations': len(self._conversations),
            'messages': len(self._messages),
            'knowledge_base': len(self._knowledge_base)
        }

# Создание глобального экземпляра для удобства
db_manager = DatabaseManager()
