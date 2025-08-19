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

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/bot_rag_simple.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN not set in .env")

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
    """Обрабатывает запрос через упрощенную RAG систему"""
    try:
        logger.info(f"Обработка RAG запроса: {question[:50]}...")
        
        # Упрощенная RAG логика - используем предопределенные ответы
        rag_responses = {
            "какие товары": "🏢 **Наши товары и услуги:**\n\n• Электроника и гаджеты\n• Компьютерная техника\n• Офисное оборудование\n• Программное обеспечение\n• Консультационные услуги\n\nДля получения подробной информации обратитесь к менеджеру.",
            "товары": "🏢 **Наши товары и услуги:**\n\n• Электроника и гаджеты\n• Компьютерная техника\n• Офисное оборудование\n• Программное обеспечение\n• Консультационные услуги\n\nДля получения подробной информации обратитесь к менеджеру.",
            "цены": "💰 **Информация о ценах:**\n\nЦены зависят от конкретного товара и объема заказа. Для получения актуальных цен и скидок свяжитесь с нашими менеджерами.\n\n📞 Контакты: +7 (XXX) XXX-XX-XX",
            "доставка": "🚚 **Условия доставки:**\n\n• Доставка по городу - 500₽\n• Доставка по области - от 1000₽\n• Самовывоз - бесплатно\n• Сроки доставки: 1-3 дня\n\nПодробности уточняйте у менеджера.",
            "контакты": "📞 **Наши контакты:**\n\n• Телефон: +7 (XXX) XXX-XX-XX\n• Email: info@company.com\n• Адрес: ул. Примерная, д. 123\n• Время работы: Пн-Пт 9:00-18:00",
            "о компании": "🏢 **О компании:**\n\nМы - надежный поставщик электроники и компьютерной техники с 10-летним опытом работы. Наша миссия - предоставлять качественные товары и отличный сервис.\n\n✅ Гарантия качества\n✅ Техническая поддержка\n✅ Гибкие условия оплаты",
            "гарантия": "🛡️ **Гарантийное обслуживание:**\n\n• Гарантия на технику: 12-36 месяцев\n• Гарантия на ПО: 6-12 месяцев\n• Бесплатная диагностика\n• Ремонт в сервисном центре\n\nПодробности уточняйте у менеджера.",
            "гарантии": "🛡️ **Гарантийное обслуживание:**\n\n• Гарантия на технику: 12-36 месяцев\n• Гарантия на ПО: 6-12 месяцев\n• Бесплатная диагностика\n• Ремонт в сервисном центре\n\nПодробности уточняйте у менеджера.",
            "оплата": "💳 **Способы оплаты:**\n\n• Наличные\n• Банковские карты\n• Безналичный расчет\n• Рассрочка (при наличии)\n\nУсловия оплаты обсуждаются индивидуально."
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
            "• О компании\n"
            "• Гарантии\n"
            "• Оплате\n\n"
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
    logger.info("Starting simple RAG bot...")
    
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
