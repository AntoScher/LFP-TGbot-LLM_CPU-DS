import hashlib
import json
import time
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class RAGCacheSystem:
    """Система кэширования для RAG ответов"""
    
    def __init__(self, cache_file: str = "rag_cache.json"):
        self.cache_file = cache_file
        self.cache: Dict[str, dict] = {}
        self.load_cache()
        
        # Предварительно подготовленные ответы для популярных запросов
        self.precomputed_answers = {
            "о компании": "🏢 **ТехноПлюс** — надежный поставщик компьютерной техники с 2010 года.\n\n• **Продукты:** Ноутбуки, ПК, серверы\n• **Услуги:** Техподдержка, гарантия\n• **Контакты:** +7 (XXX) XXX-XX-XX",
            "товары": "💻 **Наши товары:**\n\n• BusinessPro X1 - 89 990₽\n• GamerForce Z7 - 129 990₽\n• OfficeMax Pro - 79 990₽\n• GameStation Ultra - 149 990₽\n\n📞 Подробности: +7 (XXX) XXX-XX-XX",
            "цены": "💰 **Цены:**\n\n• Ноутбуки: от 89 990₽\n• Компьютеры: от 79 990₽\n• Серверы: от 199 990₽\n\n🎯 Скидки при заказе от 3 единиц\n📞 +7 (XXX) XXX-XX-XX",
            "доставка": "🚚 **Доставка:**\n\n• По городу: 500₽\n• По области: от 1 000₽\n• Самовывоз: бесплатно\n• Сроки: 1-3 дня\n\n📞 +7 (XXX) XXX-XX-XX",
            "контакты": "📞 **Контакты:**\n\n• Телефон: +7 (XXX) XXX-XX-XX\n• Email: info@technoplus.com\n• Адрес: ул. Технологическая, 15\n• Время: Пн-Пт 9:00-18:00",
            "гарантия": "🛡️ **Гарантия:**\n\n• Ноутбуки: 24-36 месяцев\n• Комплектующие: 12-24 месяца\n• Бесплатная диагностика\n• Ремонт в сервисном центре\n\n📞 +7 (XXX) XXX-XX-XX"
        }
    
    def get_question_hash(self, question: str) -> str:
        """Создает хэш для вопроса"""
        return hashlib.md5(question.lower().strip().encode()).hexdigest()
    
    def is_precomputed_question(self, question: str) -> Optional[str]:
        """Проверяет, есть ли предварительно подготовленный ответ"""
        question_lower = question.lower()
        for key, answer in self.precomputed_answers.items():
            if key in question_lower:
                logger.info(f"🚀 Найден предварительный ответ для: {key}")
                return answer
        return None
    
    def get_cached_answer(self, question: str) -> Optional[str]:
        """Получает ответ из кэша"""
        # Сначала проверяем предварительные ответы
        precomputed = self.is_precomputed_question(question)
        if precomputed:
            return precomputed
            
        # Затем проверяем кэш
        question_hash = self.get_question_hash(question)
        if question_hash in self.cache:
            cached_data = self.cache[question_hash]
            # Проверяем, не устарел ли кэш (24 часа)
            if time.time() - cached_data['timestamp'] < 86400:
                logger.info(f"📦 Найден кэшированный ответ для вопроса")
                return cached_data['answer']
        return None
    
    def cache_answer(self, question: str, answer: str):
        """Сохраняет ответ в кэш"""
        question_hash = self.get_question_hash(question)
        self.cache[question_hash] = {
            'question': question,
            'answer': answer,
            'timestamp': time.time()
        }
        self.save_cache()
        logger.info(f"💾 Ответ сохранен в кэш")
    
    def load_cache(self):
        """Загружает кэш из файла"""
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                self.cache = json.load(f)
            logger.info(f"📦 Загружен кэш с {len(self.cache)} записями")
        except FileNotFoundError:
            self.cache = {}
            logger.info("📦 Создан новый кэш")
        except Exception as e:
            logger.error(f"Ошибка загрузки кэша: {e}")
            self.cache = {}
    
    def save_cache(self):
        """Сохраняет кэш в файл"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения кэша: {e}")
    
    def clear_old_cache(self, max_age_hours: int = 168):  # 7 дней
        """Очищает устаревший кэш"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        old_keys = [
            key for key, data in self.cache.items()
            if current_time - data['timestamp'] > max_age_seconds
        ]
        
        for key in old_keys:
            del self.cache[key]
        
        if old_keys:
            self.save_cache()
            logger.info(f"🧹 Очищено {len(old_keys)} устаревших записей из кэша")

# Глобальный экземпляр кэша
rag_cache = RAGCacheSystem()
