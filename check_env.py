import os
from dotenv import load_dotenv

print("🔍 Проверка загрузки переменных из .env файла...")

# Загружаем .env файл
load_dotenv()

# Проверяем все переменные
variables = [
    "TELEGRAM_TOKEN",
    "HUGGINGFACEHUB_API_TOKEN", 
    "DEEPSEEK_API_KEY"
]

for var in variables:
    value = os.getenv(var)
    if value:
        # Показываем только начало и конец для безопасности
        masked_value = f"{value[:10]}...{value[-10:]}" if len(value) > 20 else value
        print(f"✅ {var}: {masked_value}")
    else:
        print(f"❌ {var}: НЕ НАЙДЕН")

print("\n📋 Полный список переменных окружения:")
for key, value in os.environ.items():
    if any(keyword in key.upper() for keyword in ['TOKEN', 'KEY', 'API']):
        masked_value = f"{value[:10]}...{value[-10:]}" if len(value) > 20 else value
        print(f"  {key}: {masked_value}")
