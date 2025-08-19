#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы RAG и векторной базы
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

def test_embeddings():
    """Тестируем загрузку embeddings модели"""
    try:
        from embeddings import init_vector_store
        logger.info("Тестирование embeddings модели...")
        
        retriever = init_vector_store()
        logger.info("✅ Embeddings модель загружена успешно")
        return retriever
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки embeddings: {e}")
        return None

def test_vector_search(retriever):
    """Тестируем поиск в векторной базе"""
    if not retriever:
        logger.error("❌ Ретривер не инициализирован")
        return
    
    test_queries = [
        "расскажи о компании ТехноПлюс",
        "какие ноутбуки у вас есть",
        "сколько стоит доставка",
        "какие способы оплаты",
        "акции и скидки"
    ]
    
    logger.info("🔍 Тестирование поиска в векторной базе...")
    
    for query in test_queries:
        try:
            logger.info(f"\n📝 Запрос: '{query}'")
            docs = retriever.get_relevant_documents(query)
            
            logger.info(f"📄 Найдено документов: {len(docs)}")
            
            for i, doc in enumerate(docs[:2]):  # Показываем только первые 2
                content = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                logger.info(f"  Документ {i+1}: {content}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка поиска для запроса '{query}': {e}")

def test_qa_chain():
    """Тестируем полную QA цепочку"""
    try:
        from chains import init_qa_chain
        from embeddings import init_vector_store
        
        logger.info("🧠 Тестирование QA цепочки...")
        
        # Инициализируем компоненты
        retriever = init_vector_store()
        qa_chain = init_qa_chain(retriever)
        
        test_questions = [
            "Расскажи о компании ТехноПлюс",
            "Какие ноутбуки у вас есть в наличии?",
            "Сколько стоит доставка по Москве?"
        ]
        
        for question in test_questions:
            try:
                logger.info(f"\n❓ Вопрос: {question}")
                
                # Выполняем запрос
                result = qa_chain({"question": question})
                answer = result.get("result", "").strip()
                
                logger.info(f"💬 Ответ ({len(answer)} символов):")
                logger.info(f"  {answer[:300]}{'...' if len(answer) > 300 else ''}")
                
            except Exception as e:
                logger.error(f"❌ Ошибка QA цепочки для вопроса '{question}': {e}")
                
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации QA цепочки: {e}")

def test_database_stats():
    """Проверяем статистику базы данных"""
    try:
        import sqlite3
        
        db_path = "chroma_db/chroma.sqlite3"
        if not os.path.exists(db_path):
            logger.warning("⚠️ База данных не найдена")
            return
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Получаем статистику
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        logger.info(f"📊 Таблицы в БД: {[table[0] for table in tables]}")
        
        # Проверяем количество записей в основных таблицах
        for table in ['embeddings', 'documents']:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                logger.info(f"📈 Записей в таблице {table}: {count}")
            except:
                logger.warning(f"⚠️ Таблица {table} не найдена")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Ошибка проверки БД: {e}")

def main():
    """Основная функция тестирования"""
    logger.info("🚀 Начинаем тестирование RAG системы...")
    
    # Тест 1: Embeddings модель
    retriever = test_embeddings()
    
    # Тест 2: Векторный поиск
    test_vector_search(retriever)
    
    # Тест 3: Статистика БД
    test_database_stats()
    
    # Тест 4: QA цепочка
    test_qa_chain()
    
    logger.info("✅ Тестирование завершено!")

if __name__ == "__main__":
    main()
