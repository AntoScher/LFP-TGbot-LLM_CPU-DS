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

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/bot_langchain_improved.log', encoding='utf-8')
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

def initialize_resources():
    """Инициализация RAG системы с улучшениями"""
    global qa_chain, retriever
    
    logger.info("🧠 Запуск инициализации улучшенной LangChain RAG системы...")
    
    try:
        logger.info("Инициализация улучшенной LangChain RAG системы...")
        
        # Импортируем улучшенные модули
        from embeddings import init_vector_store
        from chains_improved import init_qa_chain
        
        # Инициализация векторного хранилища
        retriever = init_vector_store()
        
        # Инициализация улучшенной QA цепи
        qa_chain = init_qa_chain(retriever)
        
        logger.info("✅ Улучшенная LangChain RAG система успешно инициализирована")
        return qa_chain, retriever
        
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации: {e}")
        raise

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    logger.info(f"Start command from user {user.id} (@{user.username})")
    
    welcome_message = (
        "🧠 **Улучшенный LangChain RAG ассистент ТехноПлюс**\n\n"
        "✨ **Возможности:**\n"
        "• 🔍 Точный векторный поиск\n"
        "• 🧠 Семантический анализ\n" 
        "• 📚 Глубокое понимание контекста\n"
        "• ⚡ Оптимизированная обработка\n\n"
        "💬 **Просто задайте вопрос о компании!**"
    )
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений с улучшенной логикой"""
    user = update.effective_user
    message_text = update.message.text
    
    logger.info(f"Message from user {user.id} (@{user.username}): {message_text}")
    
    # Отправляем сообщение о начале обработки
    processing_msg = await update.message.reply_text("🔍 **Анализирую ваш запрос...**", parse_mode='Markdown')
    
    try:
        start_time = time.time()
        
        # Предварительная фильтрация запросов
        if len(message_text.strip()) < 3:
            await processing_msg.delete()
            await update.message.reply_text(
                "❓ Пожалуйста, задайте более конкретный вопрос о компании ТехноПлюс.",
                parse_mode='Markdown'
            )
            return
            
        # Обработка через улучшенную LangChain RAG
        logger.info(f"Обработка улучшенного LangChain RAG запроса: {message_text[:50]}...")
        
        # Генерация ответа с таймаутом
        result = qa_chain.invoke({"question": message_text})
        response = result.get("result", "").strip()
        
        # Постобработка ответа
        if not response or len(response) < 10:
            response = (
                "📋 **Информация не найдена**\n\n"
                "Для получения подробной информации обратитесь к менеджеру:\n"
                "📞 +7 (XXX) XXX-XX-XX\n"
                "📧 info@technoplus.com"
            )
        else:
            # Ограничиваем длину ответа
            if len(response) > 1000:
                response = response[:1000] + "...\n\n📞 Подробности: +7 (XXX) XXX-XX-XX"
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        logger.info(f"✅ Улучшенный LangChain RAG ответ сгенерирован: {len(response)} символов за {processing_time:.1f}с")
        
        # Удаляем сообщение о загрузке и отправляем ответ
        await processing_msg.delete()
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"❌ Ошибка при обработке запроса: {e}")
        await processing_msg.delete()
        await update.message.reply_text(
            "⚠️ **Произошла ошибка при обработке запроса**\n\n"
            "Пожалуйста, попробуйте переформулировать вопрос или обратитесь к менеджеру:\n"
            "📞 +7 (XXX) XXX-XX-XX",
            parse_mode='Markdown'
        )

def main():
    """Основная функция запуска улучшенного бота"""
    try:
        # Инициализация RAG системы
        initialize_resources()
        
        logger.info("🚀 Starting improved LangChain RAG bot...")
        
        # Создание приложения
        application = Application.builder().token(TOKEN).build()
        
        # Регистрация обработчиков
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Запуск бота
        logger.info("✅ Улучшенный LangChain RAG бот готов к работе!")
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    main()
