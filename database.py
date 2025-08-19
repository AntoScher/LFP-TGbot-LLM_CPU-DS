import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Менеджер базы данных SQLite для хранения истории разговоров"""
    
    def __init__(self, db_path: str = "bot_history.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Таблица для истории разговоров
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        session_id TEXT NOT NULL,
                        mode TEXT NOT NULL,
                        user_message TEXT NOT NULL,
                        bot_response TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        response_time_ms INTEGER,
                        tokens_used INTEGER,
                        error_message TEXT
                    )
                ''')
                
                # Таблица для сессий пользователей
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER UNIQUE NOT NULL,
                        current_mode TEXT DEFAULT 'main',
                        session_start DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                        total_messages INTEGER DEFAULT 0
                    )
                ''')
                
                # Индексы для оптимизации
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON conversations(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON conversations(session_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON conversations(timestamp)')
                
                conn.commit()
                logger.info(f"База данных инициализирована: {self.db_path}")
                
        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
            raise
    
    def save_conversation(self, 
                         user_id: int, 
                         session_id: str, 
                         mode: str, 
                         user_message: str, 
                         bot_response: str,
                         response_time_ms: Optional[int] = None,
                         tokens_used: Optional[int] = None,
                         error_message: Optional[str] = None) -> bool:
        """
        Сохраняет разговор в базу данных
        
        Args:
            user_id: ID пользователя
            session_id: ID сессии
            mode: Режим работы (rag, deepseek, main)
            user_message: Сообщение пользователя
            bot_response: Ответ бота
            response_time_ms: Время ответа в миллисекундах
            tokens_used: Количество использованных токенов
            error_message: Сообщение об ошибке
            
        Returns:
            True если сохранение успешно, False в противном случае
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO conversations 
                    (user_id, session_id, mode, user_message, bot_response, 
                     response_time_ms, tokens_used, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, session_id, mode, user_message, bot_response,
                     response_time_ms, tokens_used, error_message))
                
                # Обновляем статистику пользователя
                cursor.execute('''
                    INSERT OR REPLACE INTO user_sessions 
                    (user_id, current_mode, last_activity, total_messages)
                    VALUES (?, ?, CURRENT_TIMESTAMP, 
                           COALESCE((SELECT total_messages FROM user_sessions WHERE user_id = ?), 0) + 1)
                ''', (user_id, mode, user_id))
                
                conn.commit()
                logger.info(f"Разговор сохранен для пользователя {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка сохранения разговора: {e}")
            return False
    
    def get_user_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """
        Получает историю разговоров пользователя
        
        Args:
            user_id: ID пользователя
            limit: Количество последних сообщений
            
        Returns:
            Список словарей с историей разговоров
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM conversations 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (user_id, limit))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Ошибка получения истории пользователя {user_id}: {e}")
            return []
    
    def get_user_session(self, user_id: int) -> Optional[Dict]:
        """
        Получает информацию о сессии пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Словарь с информацией о сессии или None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM user_sessions 
                    WHERE user_id = ?
                ''', (user_id,))
                
                row = cursor.fetchone()
                return dict(row) if row else None
                
        except Exception as e:
            logger.error(f"Ошибка получения сессии пользователя {user_id}: {e}")
            return None
    
    def update_user_mode(self, user_id: int, mode: str) -> bool:
        """
        Обновляет режим работы пользователя
        
        Args:
            user_id: ID пользователя
            mode: Новый режим
            
        Returns:
            True если обновление успешно
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO user_sessions 
                    (user_id, current_mode, last_activity)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, mode))
                
                conn.commit()
                logger.info(f"Режим пользователя {user_id} обновлен на {mode}")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка обновления режима пользователя {user_id}: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """
        Получает общую статистику использования бота
        
        Returns:
            Словарь со статистикой
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Общее количество сообщений
                cursor.execute('SELECT COUNT(*) FROM conversations')
                total_messages = cursor.fetchone()[0]
                
                # Количество уникальных пользователей
                cursor.execute('SELECT COUNT(DISTINCT user_id) FROM conversations')
                unique_users = cursor.fetchone()[0]
                
                # Статистика по режимам
                cursor.execute('''
                    SELECT mode, COUNT(*) as count 
                    FROM conversations 
                    GROUP BY mode
                ''')
                mode_stats = dict(cursor.fetchall())
                
                # Среднее время ответа
                cursor.execute('''
                    SELECT AVG(response_time_ms) 
                    FROM conversations 
                    WHERE response_time_ms IS NOT NULL
                ''')
                avg_response_time = cursor.fetchone()[0] or 0
                
                return {
                    'total_messages': total_messages,
                    'unique_users': unique_users,
                    'mode_stats': mode_stats,
                    'avg_response_time_ms': round(avg_response_time, 2)
                }
                
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 30) -> int:
        """
        Удаляет старые данные из базы
        
        Args:
            days: Количество дней для хранения данных
            
        Returns:
            Количество удаленных записей
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM conversations 
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"Удалено {deleted_count} старых записей")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Ошибка очистки старых данных: {e}")
            return 0
