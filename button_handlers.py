import logging
from typing import Dict, List, Optional
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Message

logger = logging.getLogger(__name__)

class ButtonHandlers:
    """Обработчики кнопок и клавиатур"""
    
    @staticmethod
    def get_main_keyboard() -> InlineKeyboardMarkup:
        """Создает главную клавиатуру с кнопкой 'Старт'"""
        keyboard = [
            [InlineKeyboardButton("🚀 Старт", callback_data="start")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_mode_selection_keyboard() -> InlineKeyboardMarkup:
        """Создает клавиатуру выбора режима"""
        keyboard = [
            [InlineKeyboardButton("🏢 О компании", callback_data="mode_rag")],
            [InlineKeyboardButton("❓ Общие вопросы", callback_data="mode_deepseek")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_back_keyboard() -> InlineKeyboardMarkup:
        """Создает клавиатуру с кнопкой 'Назад'"""
        keyboard = [
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_rag_back_keyboard() -> InlineKeyboardMarkup:
        """Создает клавиатуру для режима RAG с кнопкой 'Назад'"""
        keyboard = [
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_modes")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_deepseek_back_keyboard() -> InlineKeyboardMarkup:
        """Создает клавиатуру для режима DeepSeek с кнопкой 'Назад'"""
        keyboard = [
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_modes")]
        ]
        return InlineKeyboardMarkup(keyboard)

class UserStateManager:
    """Менеджер состояний пользователей"""
    
    def __init__(self):
        self.user_states: Dict[int, str] = {}
        self.user_sessions: Dict[int, str] = {}
    
    def set_user_state(self, user_id: int, state: str) -> None:
        """Устанавливает состояние пользователя"""
        self.user_states[user_id] = state
        logger.info(f"Пользователь {user_id} переведен в состояние: {state}")
    
    def get_user_state(self, user_id: int) -> str:
        """Получает состояние пользователя"""
        return self.user_states.get(user_id, "main")
    
    def set_user_session(self, user_id: int, session_id: str) -> None:
        """Устанавливает сессию пользователя"""
        self.user_sessions[user_id] = session_id
    
    def get_user_session(self, user_id: int) -> Optional[str]:
        """Получает сессию пользователя"""
        return self.user_sessions.get(user_id)
    
    def reset_user_state(self, user_id: int) -> None:
        """Сбрасывает состояние пользователя"""
        if user_id in self.user_states:
            del self.user_states[user_id]
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        logger.info(f"Состояние пользователя {user_id} сброшено")

class MessageHandler:
    """Обработчик сообщений и состояний"""
    
    def __init__(self, state_manager: UserStateManager):
        self.state_manager = state_manager
    
    async def handle_start_command(self, message: Message) -> tuple[str, InlineKeyboardMarkup]:
        """Обрабатывает команду /start"""
        user_id = message.from_user.id
        
        # Сбрасываем состояние пользователя
        self.state_manager.reset_user_state(user_id)
        
        welcome_text = (
            "👋 Привет! Я умный бот-помощник.\n\n"
            "Я могу помочь вам с информацией о компании или ответить на общие вопросы.\n\n"
            "Нажмите кнопку 'Старт' чтобы начать!"
        )
        
        return welcome_text, ButtonHandlers.get_main_keyboard()
    
    async def handle_start_button(self, user_id: int) -> tuple[str, InlineKeyboardMarkup]:
        """Обрабатывает нажатие кнопки 'Старт'"""
        self.state_manager.set_user_state(user_id, "mode_selection")
        
        mode_text = (
            "🎯 Выберите режим работы:\n\n"
            "🏢 **О компании** - вопросы о нашей компании, услугах и продуктах\n"
            "❓ **Общие вопросы** - любые другие вопросы и общение\n\n"
            "Выберите подходящий вариант:"
        )
        
        return mode_text, ButtonHandlers.get_mode_selection_keyboard()
    
    async def handle_mode_selection(self, user_id: int, mode: str) -> tuple[str, InlineKeyboardMarkup]:
        """Обрабатывает выбор режима"""
        if mode == "rag":
            self.state_manager.set_user_state(user_id, "rag_mode")
            rag_text = (
                "🏢 **Режим 'О компании'**\n\n"
                "Теперь вы можете задавать вопросы о нашей компании, услугах и продуктах.\n"
                "Я буду отвечать на основе локальной базы знаний.\n\n"
                "Задавайте любые вопросы!"
            )
            return rag_text, ButtonHandlers.get_rag_back_keyboard()
        
        elif mode == "deepseek":
            self.state_manager.set_user_state(user_id, "deepseek_mode")
            deepseek_text = (
                "❓ **Режим 'Общие вопросы'**\n\n"
                "Теперь вы можете задавать любые вопросы.\n"
                "Я буду отвечать с помощью DeepSeek AI.\n\n"
                "Задавайте любые вопросы!"
            )
            return deepseek_text, ButtonHandlers.get_deepseek_back_keyboard()
        
        else:
            return "❌ Неизвестный режим", ButtonHandlers.get_mode_selection_keyboard()
    
    async def handle_back_button(self, user_id: int, back_to: str) -> tuple[str, InlineKeyboardMarkup]:
        """Обрабатывает кнопку 'Назад'"""
        if back_to == "main":
            self.state_manager.reset_user_state(user_id)
            return await self.handle_start_button(user_id)
        
        elif back_to == "modes":
            self.state_manager.set_user_state(user_id, "mode_selection")
            mode_text = (
                "🎯 Выберите режим работы:\n\n"
                "🏢 **О компании** - вопросы о нашей компании, услугах и продуктах\n"
                "❓ **Общие вопросы** - любые другие вопросы и общение\n\n"
                "Выберите подходящий вариант:"
            )
            return mode_text, ButtonHandlers.get_mode_selection_keyboard()
        
        else:
            return "❌ Ошибка навигации", ButtonHandlers.get_main_keyboard()
    
    async def handle_text_message(self, user_id: int, text: str) -> tuple[str, InlineKeyboardMarkup, str]:
        """Обрабатывает текстовое сообщение в зависимости от состояния"""
        current_state = self.state_manager.get_user_state(user_id)
        
        if current_state == "main":
            # Если пользователь в главном меню, предлагаем нажать Старт
            return (
                "Нажмите кнопку 'Старт' чтобы начать работу с ботом!",
                ButtonHandlers.get_main_keyboard(),
                "main"
            )
        
        elif current_state == "mode_selection":
            # Если пользователь в выборе режима, предлагаем выбрать
            return (
                "Пожалуйста, выберите режим работы с помощью кнопок ниже:",
                ButtonHandlers.get_mode_selection_keyboard(),
                "mode_selection"
            )
        
        elif current_state == "rag_mode":
            # Обработка в режиме RAG
            return (
                text,  # Передаем текст для обработки в RAG
                ButtonHandlers.get_rag_back_keyboard(),
                "rag"
            )
        
        elif current_state == "deepseek_mode":
            # Обработка в режиме DeepSeek
            return (
                text,  # Передаем текст для обработки в DeepSeek
                ButtonHandlers.get_deepseek_back_keyboard(),
                "deepseek"
            )
        
        else:
            # Неизвестное состояние - сбрасываем
            self.state_manager.reset_user_state(user_id)
            return (
                "Произошла ошибка. Нажмите 'Старт' для начала работы.",
                ButtonHandlers.get_main_keyboard(),
                "main"
            )
