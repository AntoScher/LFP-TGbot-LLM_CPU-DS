import os
import logging
import time
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
    CommandHandler
)

# Импорты для RAG системы
from chains import init_qa_chain
from embeddings import init_vector_store

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/bot_rag_only.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN not set in .env")

# Глобальные переменные для RAG системы
qa_chain = None
vectordb = None

def get_main_keyboard():
    """Создает главную клавиатуру"""
    keyboard = [
        [InlineKeyboardButton("🏢 О компании", callback_data="start_rag")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    """Создает клавиатуру с кнопкой 'Назад'"""
    keyboard = [
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def process_rag_query(question: str) -> str:
    """Обрабатывает запрос через RAG систему"""
    global qa_chain
    
    try:
        if not qa_chain:
            logger.error("QA chain не инициализирована")
            return "❌ Ошибка: RAG система не готова. Попробуйте позже."
        
        logger.info(f"Обработка RAG запроса: {question[:50]}...")
        
        # Вызываем QA chain
        result = qa_chain({"question": question})
        
        if result and 'result' in result:
            answer = result['result'].strip()
            
            # Проверяем качество ответа
            if len(answer) < 20 or answer.lower() in ['нет информации', 'не найдено', 'не знаю']:
                logger.warning(f"Короткий или неинформативный ответ RAG: {answer}")
                return (
                    "🔍 К сожалению, в базе знаний нет информации по вашему вопросу.\n\n"
                    "Попробуйте переформулировать вопрос или обратитесь к менеджеру для получения дополнительной информации."
                )
            
            logger.info(f"RAG ответ сгенерирован: {len(answer)} символов")
            return answer
        else:
            logger.error("QA chain вернула неожиданный результат")
            return "❌ Ошибка обработки запроса. Попробуйте позже."
            
    except Exception as e:
        logger.error(f"Ошибка при обработке RAG запроса: {e}")
        return f"❌ Ошибка RAG системы: {str(e)}"

def initialize_rag_system():
    """Инициализация RAG системы"""
    global qa_chain, vectordb
    
    try:
        logger.info("Инициализация RAG системы...")
        
        # Инициализируем векторное хранилище
        retriever = init_vector_store()
        if not retriever:
            logger.error("Не удалось инициализировать векторное хранилище")
            return False
        
        # Инициализируем QA цепь
        qa_chain = init_qa_chain(retriever)
        if not qa_chain:
            logger.error("Не удалось инициализировать QA цепь")
            return False
        
        logger.info("RAG система успешно инициализирована")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка инициализации RAG системы: {e}")
        return False

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "unknown"

    logger.info(f"Start command from user {user_id} (@{username})")

    welcome_text = (
        "🏢 **Бот 'О компании'**\n\n"
        "Я могу ответить на ваши вопросы о нашей компании, услугах и продуктах.\n\n"
        "Нажмите кнопку 'О компании' чтобы начать!"
    )

    await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard())

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на кнопки"""
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username or "unknown"
    callback_data = query.data

    logger.info(f"Callback query from user {user_id} (@{username}): {callback_data}")

    try:
        if callback_data == "start_rag":
            text = (
                "🏢 **Режим 'О компании'**\n\n"
                "Теперь вы можете задавать вопросы о нашей компании, услугах и продуктах.\n"
                "Я буду отвечать на основе локальной базы знаний.\n\n"
                "Задавайте любые вопросы!"
            )
            await query.edit_message_text(text, reply_markup=get_back_keyboard())

        elif callback_data == "back_to_main":
            text = (
                "🏢 **Бот 'О компании'**\n\n"
                "Я могу ответить на ваши вопросы о нашей компании, услугах и продуктах.\n\n"
                "Нажмите кнопку 'О компании' чтобы начать!"
            )
            await query.edit_message_text(text, reply_markup=get_main_keyboard())

        else:
            logger.warning(f"Unknown callback data: {callback_data}")
            await query.answer("Неизвестная команда")

    except Exception as e:
        logger.error(f"Error handling callback query: {e}")
        await query.answer("Произошла ошибка при обработке команды")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "unknown"
    query_text = (update.message.text or '').strip()

    logger.info(f"Message from user {user_id} (@{username}): {query_text[:100]}")

    # Отправляем сообщение о том, что обрабатываем запрос
    processing_msg = await update.message.reply_text("🔍 Ищу информацию в базе знаний...")
    
    # Обрабатываем запрос через RAG
    response = process_rag_query(query_text)
    
    # Обрезка слишком длинных ответов
    if len(response) > 4000:
        response = response[:4000] + "\n\n[Ответ обрезан из-за ограничений Telegram]"
    
    # Удаляем сообщение о обработке и отправляем ответ
    await processing_msg.delete()
    await update.message.reply_text(response, reply_markup=get_back_keyboard())

def main():
    """Основная функция запуска бота"""
    # Инициализируем RAG систему
    logger.info("Запуск инициализации RAG системы...")
    rag_initialized = initialize_rag_system()
    
    if not rag_initialized:
        logger.error("RAG система не инициализирована. Бот не может работать.")
        return
    
    # Создание и настройка приложения
    application = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    logger.info("Starting RAG-only bot...")
    application.run_polling(
        poll_interval=0.5,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()
