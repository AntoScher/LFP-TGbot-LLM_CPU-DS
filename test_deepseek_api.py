import os
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Получаем API ключ
api_key = os.getenv("DEEPSEEK_API_KEY")
print(f"API Key: {api_key[:10]}...{api_key[-10:] if api_key else 'None'}")

if not api_key:
    print("❌ DEEPSEEK_API_KEY не найден в .env файле")
    exit(1)

# Тестируем API
url = "https://api.deepseek.com/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Привет! Как дела?"}],
    "temperature": 0.7,
    "max_tokens": 100,
    "stream": False
}

print("🔍 Тестируем DeepSeek API...")

try:
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    
    print(f"📊 Статус ответа: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            print(f"✅ API работает! Ответ: {content}")
        else:
            print("❌ Неожиданная структура ответа")
            print(f"Ответ: {result}")
    elif response.status_code == 401:
        print("❌ Ошибка авторизации: неверный API ключ")
        print("💡 Проверьте правильность ключа в .env файле")
    elif response.status_code == 429:
        print("⚠️ Превышен лимит запросов")
    else:
        print(f"❌ Ошибка API: {response.status_code}")
        print(f"Ответ: {response.text}")
        
except requests.exceptions.Timeout:
    print("⏰ Таймаут запроса")
except requests.exceptions.ConnectionError:
    print("🌐 Ошибка подключения к API")
except Exception as e:
    print(f"❌ Неожиданная ошибка: {e}")
