# test_settings.py
import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🔍 Тестирование импорта settings")
print("=" * 50)

# Проверка структуры
print("\n1. Проверка файлов:")
config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
files_to_check = [
    os.path.join(config_dir, '__init__.py'),
    os.path.join(config_dir, 'settings.py'),
    os.path.join(config_dir, 'config.yaml'),
]

for file_path in files_to_check:
    exists = os.path.exists(file_path)
    print(f"  {'✅' if exists else '❌'} {file_path}")

# Попытка импорта
print("\n2. Попытка импорта:")
try:
    from config.settings import settings
    print("  ✅ Импорт успешен!")
    
    # Проверка методов
    print("\n3. Проверка методов:")
    
    # get с ключом
    value = settings.get('yandex', 'api_key')
    print(f"  get('yandex', 'api_key'): {'✅' if value else '❌'}")
    
    # get без ключа
    value = settings.get('yandex')
    print(f"  get('yandex'): {'✅' if value else '❌'}")
    
    # get с default
    value = settings.get('nonexistent', 'key', 'default_value')
    print(f"  get с default: {'✅' if value == 'default_value' else '❌'}")
    
except ImportError as e:
    print(f"  ❌ Ошибка импорта: {e}")
    
    # Попробуем импортировать по-другому
    print("\n4. Альтернативный импорт:")
    try:
        import config.settings as settings_module
        print(f"  Модуль импортирован: {settings_module}")
        print(f"  Атрибуты: {dir(settings_module)}")
        
        # Проверяем наличие settings
        if hasattr(settings_module, 'settings'):
            print("  ✅ Атрибут 'settings' существует")
        else:
            print("  ❌ Атрибут 'settings' не найден")
            print("  Доступные атрибуты:")
            for attr in dir(settings_module):
                if not attr.startswith('_'):
                    print(f"    - {attr}")
    except Exception as e2:
        print(f"  ❌ Ошибка: {e2}")

# Вывод информации о Python
print(f"\n📌 Python version: {sys.version}")
print(f"📌 Текущая директория: {os.getcwd()}")