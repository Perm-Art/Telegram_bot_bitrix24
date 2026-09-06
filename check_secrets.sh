#!/bin/bash
echo "🔍 Поиск секретов в файлах..."

# Паттерны секретов
patterns=(
    "AQVN"           # Yandex API Key
    "b1g6bvts"       # Yandex Folder ID
    "8930384818"     # Telegram Token (первые цифры)
    "BEGIN.*PRIVATE" # SSH ключи
    "password.*=.*[a-zA-Z0-9]\{8,\}"  # Пароли
)

for pattern in "${patterns[@]}"; do
    echo "Проверка: $pattern"
    grep -r "$pattern" --exclude-dir=.git --exclude-dir=venv --exclude=.env .
    if [ $? -eq 0 ]; then
        echo "⚠️ Найдены совпадения!"
    else
        echo "✅ Чисто"
    fi
done