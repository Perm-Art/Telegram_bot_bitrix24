from yandex_assistant.yandex_gpt5 import YandexGPT5
from config.settings import settings

# Инициализация
gpt = YandexGPT5(
    api_key=settings.get('yandex', 'api_key'),
    folder_id=settings.get('yandex', 'folder_id'),
    model=settings.get('yandex', 'model')
)

# Тестовый запрос
print("🚀 Тестирование Yandex GPT 5.1")
print("=" * 50)

response = gpt.generate_response(
    prompt="Что такое REST API в Bitrix24?",
    max_tokens=500
)

print("Ответ:")
print("-" * 50)
print(response)
print("-" * 50)
