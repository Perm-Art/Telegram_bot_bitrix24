import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

class Settings:
    """Класс для управления настройками"""
    
    def __init__(self):
        self.config = {
            'telegram': {
                'token': os.getenv('TELEGRAM_TOKEN', ''),
                'allowed_users': []
            },
            'yandex': {
                'api_key': os.getenv('YANDEX_API_KEY', ''),
                'folder_id': os.getenv('YANDEX_FOLDER_ID', ''),
                'model': os.getenv('YANDEX_MODEL', 'yandexgpt-5.1/latest'),
                'base_url': 'https://ai.api.cloud.yandex.net/v1'
            },
            'database': {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', '5432')),
                'name': os.getenv('DB_NAME', 'bitrix24_assistant'),
                'user': os.getenv('DB_USER', 'bot_user'),
                'password': os.getenv('DB_PASSWORD', '')
            },
            'parser': {
                'base_url': os.getenv('PARSER_BASE_URL', 'https://apidocs.bitrix24.ru/'),
                'max_pages': int(os.getenv('PARSER_MAX_PAGES', '100')),
                'update_interval_hours': int(os.getenv('PARSER_UPDATE_INTERVAL', '24'))
            },
            'logging': {
                'level': os.getenv('LOG_LEVEL', 'INFO'),
                'file': os.getenv('LOG_FILE', 'logs/bot.log')
            }
        }
    
    def get(self, section, key=None, default=None):
        """Получение значения настройки"""
        if key:
            return self.config.get(section, {}).get(key, default)
        return self.config.get(section, default)

# Создание глобального экземпляра
settings = Settings()
