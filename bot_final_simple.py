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
import requests

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/bot_final_simple.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN not set in .env")
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY not set in .env")

# Менеджер состояний пользователей
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

def call_deepseek_api(message: str) -> str:
    """Вызывает DeepSeek API"""
    try:
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": message}],
            "temperature": 0.7,
            "max_tokens": 1000,
            "stream": False
        }
        
        logger.info(f"Отправка запроса к DeepSeek API: {message[:50]}...")
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                logger.info(f"Успешный ответ от DeepSeek API: {len(content)} символов")
                return content
            else:
                logger.error("Неожиданная структура ответа от DeepSeek API")
                return "❌ Ошибка: неожиданная структура ответа от API"
                
        elif response.status_code == 401:
            logger.error("Ошибка авторизации DeepSeek API: неверный API ключ")
            return "❌ Ошибка авторизации API. Проверьте настройки."
            
        elif response.status_code == 429:
            logger.warning("Rate limit превышен")
            return "⚠️ Превышен лимит запросов. Попробуйте позже."
            
        elif response.status_code >= 500:
            logger.warning(f"Ошибка сервера DeepSeek API: {response.status_code}")
            return "🔧 Сервис временно недоступен. Попробуйте позже."
            
        else:
            logger.error(f"Ошибка DeepSeek API: {response.status_code} - {response.text}")
            return f"❌ Ошибка API: {response.status_code}"
            
    except requests.exceptions.Timeout:
        logger.warning("Таймаут запроса к DeepSeek API")
        return "⏰ Превышено время ожидания ответа. Попробуйте позже."
        
    except requests.exceptions.ConnectionError:
        logger.warning("Ошибка подключения к DeepSeek API")
        return "🌐 Ошибка подключения к сервису. Проверьте интернет-соединение."
        
    except Exception as e:
        logger.error(f"Неожиданная ошибка при запросе к DeepSeek API: {e}")
        return f"❌ Неожиданная ошибка: {str(e)}"

def process_rag_query(question: str) -> str:
    """Обрабатывает запрос через RAG систему (упрощенная версия)"""
    try:
        logger.info(f"Обработка RAG запроса: {question[:50]}...")
        
        # Упрощенная RAG логика - используем предопределенные ответы
        rag_responses = {
            "какие товары": "🏢 **Наши товары и услуги:**\n\n• Электроника и гаджеты\n• Компьютерная техника\n• Офисное оборудование\n• Программное обеспечение\n• Консультационные услуги\n\nДля получения подробной информации обратитесь к менеджеру.",
            "цены": "💰 **Информация о ценах:**\n\nЦены зависят от конкретного товара и объема заказа. Для получения актуальных цен и скидок свяжитесь с нашими менеджерами.\n\n📞 Контакты: +7 (XXX) XXX-XX-XX",
            "доставка": "🚚 **Условия доставки:**\n\n• Доставка по городу - 500₽\n• Доставка по области - от 1000₽\n• Самовывоз - бесплатно\n• Сроки доставки: 1-3 дня\n\nПодробности уточняйте у менеджера.",
            "контакты": "📞 **Наши контакты:**\n\n• Телефон: +7 (XXX) XXX-XX-XX\n• Email: info@company.com\n• Адрес: ул. Примерная, д. 123\n• Время работы: Пн-Пт 9:00-18:00",
            "о компании": "🏢 **О компании:**\n\nМы - надежный поставщик электроники и компьютерной техники с 10-летним опытом работы. Наша миссия - предоставлять качественные товары и отличный сервис.\n\n✅ Гарантия качества\n✅ Техническая поддержка\n✅ Гибкие условия оплаты"
        }
        
        question_lower = question.lower()
        
        # Ищем подходящий ответ
        for key, response in rag_responses.items():
            if key in question_lower:
                logger.info(f"Найден RAG ответ для ключа: {key}")
                return response
        
        # Если не найдено, возвращаем общий ответ
        logger.info("RAG ответ не найден, возвращаем общий ответ")
        return (
            "🔍 **Информация о компании:**\n\n"
            "К сожалению, у меня нет подробной информации по вашему вопросу.\n\n"
            "Попробуйте задать вопрос о:\n"
            "• Товарах и услугах\n"
            "• Ценах\n"
            "• Доставке\n"
            "• Контактах\n"
            "• О компании\n\n"
            "Или обратитесь к менеджеру для получения дополнительной информации."
        )
        
    except Exception as e:
        logger.error(f"Ошибка при обработке RAG запроса: {e}")
        return f"❌ Ошибка RAG системы: {str(e)}"

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
        # Отправляем сообщение о том, что обрабатываем запрос
        processing_msg = await update.message.reply_text("🔍 Ищу информацию в базе знаний...")
        
        # Обрабатываем запрос через RAG (синхронно)
        response = process_rag_query(query_text)
        
        # Обрезка слишком длинных ответов
        if len(response) > 4000:
            response = response[:4000] + "\n\n[Ответ обрезан из-за ограничений Telegram]"
        
        # Удаляем сообщение о обработке и отправляем ответ
        await processing_msg.delete()
        await update.message.reply_text(response, reply_markup=get_back_keyboard())

    elif current_state == "deepseek_mode":
        # Отправляем сообщение о том, что обрабатываем запрос
        processing_msg = await update.message.reply_text("⏳ Обрабатываю ваш запрос...")
        
        # Вызываем DeepSeek API (синхронно)
        api_response = call_deepseek_api(query_text)
        
        # Обрезка слишком длинных ответов
        if len(api_response) > 4000:
            api_response = api_response[:4000] + "\n\n[Ответ обрезан из-за ограничений Telegram]"
        
        # Удаляем сообщение о обработке и отправляем ответ
        await processing_msg.delete()
        await update.message.reply_text(api_response, reply_markup=get_back_keyboard())

    else:
        user_states[user_id] = "main"
        await update.message.reply_text(
            "Произошла ошибка. Нажмите 'Старт' для начала работы.",
            reply_markup=get_main_keyboard()
        )

def main():
    """Основная функция запуска бота"""
    logger.info("Starting simplified final bot with RAG and DeepSeek API integration...")
    
    # Создание и настройка приложения
    application = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    application.run_polling(
        poll_interval=0.5,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()
