import os
import logging
import asyncio
import uuid
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

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/bot_simple_test.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN not set in .env")

# Простой менеджер состояний
user_states = {}

def get_main_keyboard():
    """Создает главную клавиатуру с кнопкой 'Старт'"""
    keyboard = [
        [InlineKeyboardButton("🚀 Старт", callback_data="start")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_mode_selection_keyboard():
    """Создает клавиатуру выбора режима"""
    keyboard = [
        [InlineKeyboardButton("🏢 О компании", callback_data="mode_rag")],
        [InlineKeyboardButton("❓ Общие вопросы", callback_data="mode_deepseek")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    """Создает клавиатуру с кнопкой 'Назад'"""
    keyboard = [
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_modes")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "unknown"

    logger.info(f"Start command from user {user_id} (@{username})")

    # Сбрасываем состояние пользователя
    user_states[user_id] = "main"

    welcome_text = (
        "👋 Привет! Я умный бот-помощник.\n\n"
        "Я могу помочь вам с информацией о компании или ответить на общие вопросы.\n\n"
        "Нажмите кнопку 'Старт' чтобы начать!"
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
        if callback_data == "start":
            user_states[user_id] = "mode_selection"
            text = (
                "🎯 Выберите режим работы:\n\n"
                "🏢 **О компании** - вопросы о нашей компании, услугах и продуктах\n"
                "❓ **Общие вопросы** - любые другие вопросы и общение\n\n"
                "Выберите подходящий вариант:"
            )
            await query.edit_message_text(text, reply_markup=get_mode_selection_keyboard())

        elif callback_data == "mode_rag":
            user_states[user_id] = "rag_mode"
            text = (
                "🏢 **Режим 'О компании'**\n\n"
                "Теперь вы можете задавать вопросы о нашей компании, услугах и продуктах.\n"
                "Я буду отвечать на основе локальной базы знаний.\n\n"
                "Задавайте любые вопросы!"
            )
            await query.edit_message_text(text, reply_markup=get_back_keyboard())

        elif callback_data == "mode_deepseek":
            user_states[user_id] = "deepseek_mode"
            text = (
                "❓ **Режим 'Общие вопросы'**\n\n"
                "Теперь вы можете задавать любые вопросы.\n"
                "Я буду отвечать с помощью DeepSeek AI.\n\n"
                "Задавайте любые вопросы!"
            )
            await query.edit_message_text(text, reply_markup=get_back_keyboard())

        elif callback_data == "back_to_modes":
            user_states[user_id] = "mode_selection"
            text = (
                "🎯 Выберите режим работы:\n\n"
                "🏢 **О компании** - вопросы о нашей компании, услугах и продуктах\n"
                "❓ **Общие вопросы** - любые другие вопросы и общение\n\n"
                "Выберите подходящий вариант:"
            )
            await query.edit_message_text(text, reply_markup=get_mode_selection_keyboard())

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

    current_state = user_states.get(user_id, "main")

    if current_state == "main":
        await update.message.reply_text(
            "Нажмите кнопку 'Старт' чтобы начать работу с ботом!",
            reply_markup=get_main_keyboard()
        )

    elif current_state == "mode_selection":
        await update.message.reply_text(
            "Пожалуйста, выберите режим работы с помощью кнопок ниже:",
            reply_markup=get_mode_selection_keyboard()
        )

    elif current_state == "rag_mode":
        # Простой ответ для тестирования
        response = f"🔍 **Режим RAG**\n\nВаш вопрос: '{query_text}'\n\nЭто тестовый ответ. В реальной версии здесь будет RAG система."
        await update.message.reply_text(response, reply_markup=get_back_keyboard())

    elif current_state == "deepseek_mode":
        # Простой ответ для тестирования
        response = f"🤖 **Режим DeepSeek**\n\nВаш вопрос: '{query_text}'\n\nЭто тестовый ответ. В реальной версии здесь будет DeepSeek API."
        await update.message.reply_text(response, reply_markup=get_back_keyboard())

    else:
        user_states[user_id] = "main"
        await update.message.reply_text(
            "Произошла ошибка. Нажмите 'Старт' для начала работы.",
            reply_markup=get_main_keyboard()
        )

def main():
    """Основная функция запуска бота"""
    # Создание и настройка приложения
    application = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    logger.info("Starting simple test bot...")
    application.run_polling(
        poll_interval=0.5,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()
