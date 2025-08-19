import os
import time
import requests
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from pathlib import Path

# Настройка логирования
logger = logging.getLogger(__name__)

# Загружаем .env файл
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path, encoding='utf-8-sig')

class DeepSeekClient:
    """Клиент для работы с DeepSeek API"""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            logger.error("DEEPSEEK_API_KEY не найден в .env файле")
            raise ValueError("DEEPSEEK_API_KEY environment variable not set")
        
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.timeout = 60
        self.max_retries = 3
        self.retry_delay = 2
        
        logger.info(f"DeepSeek клиент инициализирован: {self.api_key[:5]}...{self.api_key[-5:]}")
    
    def generate_response(self, 
                         message: str, 
                         max_tokens: int = 1024, 
                         temperature: float = 0.7,
                         model: str = "deepseek-chat") -> Optional[str]:
        """
        Генерирует ответ через DeepSeek API
        
        Args:
            message: Входящее сообщение
            max_tokens: Максимальное количество токенов
            temperature: Температура генерации
            model: Модель для использования
            
        Returns:
            Сгенерированный ответ или None в случае ошибки
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": message}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        # Попытки с повторениями
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Отправка запроса к DeepSeek API (попытка {attempt + 1}/{self.max_retries})")
                
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        content = result['choices'][0]['message']['content']
                        logger.info(f"Успешный ответ от DeepSeek API: {len(content)} символов")
                        return content
                    else:
                        logger.error("Неожиданная структура ответа от DeepSeek API")
                        return None
                
                elif response.status_code == 401:
                    logger.error("Ошибка авторизации DeepSeek API: неверный API ключ")
                    return "❌ Ошибка авторизации API. Проверьте настройки."
                
                elif response.status_code == 429:
                    logger.warning(f"Rate limit превышен (попытка {attempt + 1})")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    return "⚠️ Превышен лимит запросов. Попробуйте позже."
                
                elif response.status_code >= 500:
                    logger.warning(f"Ошибка сервера DeepSeek API: {response.status_code} (попытка {attempt + 1})")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    return "🔧 Сервис временно недоступен. Попробуйте позже."
                
                else:
                    logger.error(f"Ошибка DeepSeek API: {response.status_code} - {response.text}")
                    return f"❌ Ошибка API: {response.status_code}"
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Таймаут запроса к DeepSeek API (попытка {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                return "⏰ Превышено время ожидания ответа. Попробуйте позже."
                
            except requests.exceptions.ConnectionError:
                logger.warning(f"Ошибка подключения к DeepSeek API (попытка {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                return "🌐 Ошибка подключения к сервису. Проверьте интернет-соединение."
                
            except Exception as e:
                logger.error(f"Неожиданная ошибка при запросе к DeepSeek API: {e}")
                return f"❌ Неожиданная ошибка: {str(e)}"
        
        return "❌ Не удалось получить ответ после всех попыток"
    
    def is_available(self) -> bool:
        """Проверяет доступность DeepSeek API"""
        try:
            response = requests.get(
                "https://api.deepseek.com/v1/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
