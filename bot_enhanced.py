import os
import logging
import traceback
import asyncio
import uuid
import time
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
    CommandHandler
)

# Импорты наших модулей
from button_handlers import ButtonHandlers, UserStateManager, MessageHandler as StateMessageHandler
from database import DatabaseManager
from deepseek_client import DeepSeekClient
from embeddings import init_vector_store, VectorStoreInitializationError
from chains import init_qa_chain

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/bot_enhanced.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Глобальные переменные
retriever = None
qa_chain = None
is_initialized = False
initialization_error = None

# Инициализация менеджеров
state_manager = UserStateManager()
message_handler = StateMessageHandler(state_manager)
db_manager = DatabaseManager()
deepseek_client = None

def setup_environment():
    """Настройка окружения и загрузка конфигурации"""
    global deepseek_client
    
    try:
        # Загрузка переменных окружения
        if not load_dotenv():
            logger.warning("No .env file found or it's empty")
            
        # Проверка обязательных переменных окружения
        required_vars = ["TELEGRAM_TOKEN", "HUGGINGFACEHUB_API_TOKEN"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Инициализация DeepSeek клиента
        try:
            deepseek_client = DeepSeekClient()
            logger.info("DeepSeek client initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize DeepSeek client: {e}")
            deepseek_client = None
            
        logger.info("Environment setup completed successfully")
        
    except Exception as e:
        logger.critical(f"Critical error during environment setup: {str(e)}")
        logger.critical(traceback.format_exc())
        raise

# Инициализация окружения при импорте модуля
try:
    setup_environment()
except Exception as e:
    logger.critical("Failed to initialize environment. Bot cannot start.")
    raise

# Загрузка конфигурации
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN not set in .env")

async def initialize_resources():
    """Асинхронная инициализация ресурсов бота"""
    global retriever, qa_chain, is_initialized, initialization_error
    
    try:
        logger.info("Starting resource initialization...")
        
        # Сброс состояния
        is_initialized = False
        initialization_error = None
        
        # Инициализация векторного хранилища
        try:
            logger.info("Initializing vector store...")
            retriever = await asyncio.to_thread(init_vector_store)
            if not retriever:
                raise ValueError("Vector store initialization returned None")
            logger.info("Vector store initialized successfully")
            
        except VectorStoreInitializationError as e:
            error_msg = f"Failed to initialize vector store: {str(e)}"
            logger.error(error_msg)
            initialization_error = error_msg
            return False
            
        except Exception as e:
            error_msg = f"Unexpected error initializing vector store: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            initialization_error = error_msg
            return False
        
        # Инициализация QA цепи
        try:
            logger.info("Initializing QA chain...")
            qa_chain = await asyncio.to_thread(init_qa_chain, retriever)
            if not qa_chain:
                raise ValueError("QA chain initialization returned None")
            logger.info("QA chain initialized successfully")
            
        except Exception as e:
            error_msg = f"Failed to initialize QA chain: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            initialization_error = error_msg
            return False
        
        # Успешное завершение инициализации
        is_initialized = True
        logger.info("Resource initialization completed successfully")
        return True
        
    except Exception as e:
        error_msg = f"Critical error during resource initialization: {str(e)}"
        logger.critical(error_msg)
        logger.critical(traceback.format_exc())
        initialization_error = error_msg
        return False

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "unknown"
    
    logger.info(f"Start command from user {user_id} (@{username})")
    
    # Сбрасываем состояние пользователя
    state_manager.reset_user_state(user_id)
    
    # Создаем новую сессию
    session_id = str(uuid.uuid4())
    state_manager.set_user_session(user_id, session_id)
    
    # Получаем приветственное сообщение и клавиатуру
    welcome_text, keyboard = await message_handler.handle_start_command(update.message)
    
    await update.message.reply_text(welcome_text, reply_markup=keyboard)

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на кнопки"""
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username or "unknown"
    callback_data = query.data
    
    logger.info(f"Callback query from user {user_id} (@{username}): {callback_data}")
    
    try:
        # Обработка различных callback_data
        if callback_data == "start":
            text, keyboard = await message_handler.handle_start_button(user_id)
            await query.edit_message_text(text, reply_markup=keyboard)
            
        elif callback_data == "mode_rag":
            text, keyboard = await message_handler.handle_mode_selection(user_id, "rag")
            await query.edit_message_text(text, reply_markup=keyboard)
            
        elif callback_data == "mode_deepseek":
            text, keyboard = await message_handler.handle_mode_selection(user_id, "deepseek")
            await query.edit_message_text(text, reply_markup=keyboard)
            
        elif callback_data == "back_to_main":
            text, keyboard = await message_handler.handle_back_button(user_id, "main")
            await query.edit_message_text(text, reply_markup=keyboard)
            
        elif callback_data == "back_to_modes":
            text, keyboard = await message_handler.handle_back_button(user_id, "modes")
            await query.edit_message_text(text, reply_markup=keyboard)
            
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
    
    # Получаем текущее состояние пользователя
    current_state = state_manager.get_user_state(user_id)
    session_id = state_manager.get_user_session(user_id)
    
    if not session_id:
        session_id = str(uuid.uuid4())
        state_manager.set_user_session(user_id, session_id)
    
    # Обрабатываем сообщение в зависимости от состояния
    response_text, keyboard, mode = await message_handler.handle_text_message(user_id, query_text)
    
    # Если это не просто навигационное сообщение, обрабатываем запрос
    if mode in ["rag", "deepseek"] and len(query_text) > 3:
        start_time = time.time()
        
        try:
            # Отправляем уведомление о начале обработки
            processing_msg = await update.message.reply_text("⏳ Обрабатываю ваш запрос...")
            
            if mode == "rag":
                # Обработка в режиме RAG
                if not is_initialized or not qa_chain:
                    error_msg = "RAG система не инициализирована. Попробуйте позже."
                    await processing_msg.edit_text(error_msg)
                    return
                
                # Выполняем RAG запрос
                result = await asyncio.to_thread(lambda: qa_chain({"question": query_text}))
                answer = result.get("result", "").strip()
                
                if not answer or len(answer) < 20:
                    answer = "Извините, не удалось найти информацию по вашему вопросу. Попробуйте переформулировать."
                
            elif mode == "deepseek":
                # Обработка в режиме DeepSeek
                if not deepseek_client:
                    error_msg = "DeepSeek API недоступен. Попробуйте режим 'О компании'."
                    await processing_msg.edit_text(error_msg)
                    return
                
                # Выполняем DeepSeek запрос
                answer = deepseek_client.generate_response(query_text)
                
                if not answer or answer.startswith("❌") or answer.startswith("⚠️") or answer.startswith("🔧"):
                    # Если произошла ошибка API
                    await processing_msg.edit_text(answer)
                    return
            
            # Обрезка слишком длинных ответов
            if len(answer) > 4000:
                answer = answer[:4000] + "\n\n[Ответ обрезан из-за ограничений Telegram]"
            
            # Очистка ответа
            answer = answer.replace("<|im_start|>", "").replace("<|im_end|>", "").strip()
            import re
            answer = re.sub(r'\s+', ' ', answer).strip()
            
            # Вычисляем время ответа
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Сохраняем в базу данных
            db_manager.save_conversation(
                user_id=user_id,
                session_id=session_id,
                mode=mode,
                user_message=query_text,
                bot_response=answer,
                response_time_ms=response_time_ms
            )
            
            # Отправляем ответ
            await processing_msg.edit_text(answer, reply_markup=keyboard)
            
        except Exception as e:
            error_msg = f"Ошибка при обработке запроса: {str(e)}"
            logger.error(f"Error processing message: {error_msg}")
            logger.error(traceback.format_exc())
            
            # Сохраняем ошибку в базу
            db_manager.save_conversation(
                user_id=user_id,
                session_id=session_id,
                mode=mode,
                user_message=query_text,
                bot_response="Ошибка обработки",
                error_message=error_msg
            )
            
            await update.message.reply_text(
                "Произошла ошибка при обработке запроса. Попробуйте позже.",
                reply_markup=keyboard
            )
    else:
        # Простое навигационное сообщение
        await update.message.reply_text(response_text, reply_markup=keyboard)

async def post_init(application: Application) -> None:
    """Post-initialization hook для Telegram бота"""
    global is_initialized, initialization_error
    
    try:
        logger.info("Starting bot initialization...")
        
        # Инициализация ресурсов
        success = await initialize_resources()
        
        if not success:
            error_msg = (
                "⚠️ Не удалось инициализировать бота. "
                f"Причина: {initialization_error or 'неизвестная ошибка'}"
            )
            logger.critical("Bot initialization failed")
            
            # Уведомляем админа
            admin_id = os.getenv("ADMIN_TELEGRAM_ID")
            if admin_id and admin_id.isdigit():
                try:
                    await application.bot.send_message(
                        chat_id=int(admin_id),
                        text=f"❌ Ошибка инициализации бота: {initialization_error or 'Неизвестная ошибка'}"
                    )
                except Exception as e:
                    logger.error(f"Failed to send error notification to admin: {str(e)}")
            
            raise RuntimeError(f"Bot initialization failed: {initialization_error}")
            
        logger.info("Bot initialization completed successfully")
        
        # Уведомляем админа об успешном запуске
        admin_id = os.getenv("ADMIN_TELEGRAM_ID")
        if admin_id and admin_id.isdigit():
            try:
                await application.bot.send_message(
                    chat_id=int(admin_id),
                    text="✅ Бот успешно запущен и готов к работе!"
                )
            except Exception as e:
                logger.warning(f"Failed to send startup notification to admin: {str(e)}")
                
    except Exception as e:
        logger.critical(f"Critical error in post_init: {str(e)}")
        logger.critical(traceback.format_exc())
        raise

def main():
    """Основная функция запуска бота"""
    # Создание и настройка приложения
    application = Application.builder().token(TOKEN).post_init(post_init).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    logger.info("Starting enhanced bot...")
    application.run_polling(
        poll_interval=0.5,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()
