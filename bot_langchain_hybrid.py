import os
import logging
import time
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
    ContextTypes,
    CommandHandler
)
from rag_cache_system import rag_cache

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/bot_langchain_hybrid.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN not set in .env")

# Глобальные переменные
qa_chain = None
retriever = None
use_full_rag = True  # Флаг для переключения между кэшем и полным RAG

def initialize_resources():
    """Инициализация гибридной RAG системы"""
    global qa_chain, retriever
    
    logger.info("🔥 Запуск инициализации гибридной LangChain RAG системы...")
    
    try:
        from embeddings import init_vector_store
        from chains_improved import init_qa_chain
        
        # Инициализация векторного хранилища
        retriever = init_vector_store()
        
        # Инициализация QA цепи (только если нужно)
        if use_full_rag:
            qa_chain = init_qa_chain(retriever)
        
        # Очистка старого кэша
        rag_cache.clear_old_cache()
        
        logger.info("✅ Гибридная LangChain RAG система инициализирована")
        return qa_chain, retriever
        
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации: {e}")
        raise

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    logger.info(f"Start command from user {user.id} (@{user.username})")
    
    welcome_message = (
        "🔥 **Гибридный LangChain RAG ассистент ТехноПлюс**\n\n"
        "⚡ **Возможности:**\n"
        "• 🚀 Мгновенные ответы (кэш)\n"
        "• 🧠 Глубокий анализ (при необходимости)\n" 
        "• 📚 Умное переключение режимов\n"
        "• 🎯 Оптимизированная обработка\n\n"
        "💬 **Просто задайте вопрос о компании!**"
    )
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Гибридная обработка сообщений: кэш → быстрый RAG → полный RAG"""
    user = update.effective_user
    message_text = update.message.text
    
    logger.info(f"Message from user {user.id} (@{user.username}): {message_text}")
    
    try:
        start_time = time.time()
        
        # ЭТАП 1: Проверяем кэш и предварительные ответы
        cached_answer = rag_cache.get_cached_answer(message_text)
        if cached_answer:
            end_time = time.time()
            logger.info(f"🚀 Мгновенный ответ из кэша за {end_time - start_time:.2f}с")
            await update.message.reply_text(cached_answer, parse_mode='Markdown')
            return
        
        # ЭТАП 2: Отправляем сообщение о поиске
        processing_msg = await update.message.reply_text(
            "🔍 **Ищу информацию в базе знаний...**", 
            parse_mode='Markdown'
        )
        
        # ЭТАП 3: Простой векторный поиск без LLM
        try:
            # Получаем релевантные документы
            docs = retriever.get_relevant_documents(message_text)
            
            if docs:
                # Простая обработка документов без LLM
                context = "\n".join([doc.page_content[:200] for doc in docs[:2]])
                
                # Создаем простой ответ на основе найденных документов
                simple_answer = f"📋 **Найденная информация:**\n\n{context[:500]}...\n\n📞 Подробности: +7 (XXX) XXX-XX-XX"
                
                # Кэшируем ответ
                rag_cache.cache_answer(message_text, simple_answer)
                
                end_time = time.time()
                logger.info(f"⚡ Быстрый RAG ответ за {end_time - start_time:.2f}с")
                
                await processing_msg.delete()
                await update.message.reply_text(simple_answer, parse_mode='Markdown')
                return
        except Exception as e:
            logger.warning(f"Ошибка быстрого RAG: {e}")
        
        # ЭТАП 4: Полный LangChain RAG (только для сложных случаев)
        if qa_chain and len(message_text) > 20:  # Только для детальных вопросов
            try:
                await processing_msg.edit_text(
                    "🧠 **Выполняю глубокий анализ...**", 
                    parse_mode='Markdown'
                )
                
                result = qa_chain.invoke({"question": message_text})
                response = result.get("result", "").strip()
                
                if response and len(response) > 10:
                    # Кэшируем полный ответ
                    rag_cache.cache_answer(message_text, response)
                    
                    end_time = time.time()
                    logger.info(f"🧠 Полный LangChain ответ за {end_time - start_time:.1f}с")
                    
                    await processing_msg.delete()
                    await update.message.reply_text(response, parse_mode='Markdown')
                    return
            except Exception as e:
                logger.error(f"Ошибка полного RAG: {e}")
        
        # ЭТАП 5: Fallback ответ
        fallback_answer = (
            "📋 **Информация не найдена**\n\n"
            "Для получения подробной информации обратитесь к менеджеру:\n"
            "📞 +7 (XXX) XXX-XX-XX\n"
            "📧 info@technoplus.com"
        )
        
        await processing_msg.delete()
        await update.message.reply_text(fallback_answer, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        await update.message.reply_text(
            "⚠️ **Произошла ошибка**\n\n📞 Обратитесь к менеджеру: +7 (XXX) XXX-XX-XX",
            parse_mode='Markdown'
        )

def main():
    """Основная функция запуска гибридного бота"""
    try:
        # Инициализация гибридной системы
        initialize_resources()
        
        logger.info("🔥 Starting hybrid LangChain RAG bot...")
        
        # Создание приложения
        application = Application.builder().token(TOKEN).build()
        
        # Регистрация обработчиков
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Запуск бота
        logger.info("✅ Гибридный LangChain RAG бот готов к работе!")
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    main()
