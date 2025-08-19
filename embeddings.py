import os
import logging
import traceback
from functools import lru_cache
from typing import Optional, Any
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema.vectorstore import VectorStoreRetriever
import traceback

logger = logging.getLogger(__name__)

class VectorStoreInitializationError(Exception):
    """Custom exception for vector store initialization errors"""
    pass


@lru_cache(maxsize=1)
def init_vector_store(persist_dir: Optional[str] = None) -> VectorStoreRetriever:
    """
    Инициализирует или загружает векторное хранилище Chroma.
    
    Args:
        persist_dir: Директория для сохранения векторной БД
        
    Returns:
        VectorStoreRetriever: Инициализированный ретривер для поиска
        
    Raises:
        VectorStoreInitializationError: Если не удалось инициализировать хранилище
    """
    try:
        # Разрешаем путь из переменных окружения
        if not persist_dir:
            persist_dir = (
                os.getenv("PERSIST_DIRECTORY")
                or os.getenv("CHROMA_DB_PATH")
                or "./chroma_db"
            )

        logger.info(f"Initializing vector store in directory: {persist_dir}")
        
        # Проверяем доступность директории
        os.makedirs(persist_dir, exist_ok=True)
        
        # Инициализируем модель эмбеддингов
        try:
            logger.info("Loading HuggingFace embeddings model...")
            embedder = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"}  # Явно указываем CPU для совместимости
            )
            logger.info("Embeddings model loaded successfully")
        except Exception as e:
            error_msg = f"Failed to load embeddings model: {str(e)}"
            logger.error(error_msg)
            raise VectorStoreInitializationError(error_msg) from e
        
        # Проверяем существование базы данных
        db_exists = os.path.exists(persist_dir) and os.listdir(persist_dir)
        
        if db_exists:
            try:
                logger.info("Loading existing vector database...")
                vectordb = Chroma(
                    persist_directory=persist_dir,
                    embedding_function=embedder
                )
                retriever = vectordb.as_retriever(
                    search_type="similarity",  # Используем similarity вместо mmr для более точного поиска
                    search_kwargs={
                        "k": 2  # Уменьшаем количество документов
                    }
                )
                logger.info("Vector database loaded successfully")
                return retriever
            except Exception as e:
                error_msg = f"Failed to load existing vector database: {str(e)}"
                logger.error(error_msg)
                logger.error(traceback.format_exc())
                # Продолжаем создание новой БД в случае ошибки загрузки
                logger.warning("Creating new vector database due to loading error")
        
        # Создаем новую пустую базу данных без добавления фиктивного документа
        try:
            logger.info("Creating new empty vector database...")
            vectordb = Chroma(
                embedding_function=embedder,
                persist_directory=persist_dir
            )
            vectordb.persist()
            
            retriever = vectordb.as_retriever(
                search_type="similarity",  # Используем similarity вместо mmr для более точного поиска
                search_kwargs={
                    "k": 2  # Уменьшаем количество документов
                }
            )
            
            logger.info("New empty vector database created successfully")
            return retriever
            
        except Exception as e:
            error_msg = f"Failed to create new vector database: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            raise VectorStoreInitializationError(error_msg) from e
            
    except Exception as e:
        error_msg = f"Critical error in vector store initialization: {str(e)}"
        logger.critical(error_msg)
        logger.critical(traceback.format_exc())
        raise VectorStoreInitializationError(error_msg) from e