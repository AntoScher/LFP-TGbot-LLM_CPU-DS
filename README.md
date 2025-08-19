# AI-ассистент для отдела продаж (CPU-оптимизированная версия)

Telegram-бот с RAG-архитектурой для ответов на вопросы клиентов с использованием:
- Языковой модели Qwen2-1.5B-Instruct (оптимизировано для CPU)
- Векторного поиска по базе знаний (ChromaDB)
- Логирования диалогов в SQLite/PostgreSQL

## 🚀 Возможности

- **RAG-архитектура**: Поиск релевантной информации в базе знаний
- **CPU-оптимизация**: Полностью оптимизировано для работы на CPU
- **Логирование**: Сохранение всех диалогов в базу данных
- **Простота**: Минимальные зависимости, легкая настройка
- **Стабильность**: Без экспериментальных функций

## 📋 Требования

- Python 3.10+ (рекомендуется 3.10)
- 4+ GB RAM (для работы с 1.5B-моделью на CPU)
- CPU с поддержкой AVX/AVX2 (большинство современных процессоров)

## 🛠️ Установка

### 1. Клонирование репозитория
```bash
git clone https://github.com/yourusername/LFP-TGbot-LLM-RAG.git
cd LFP-TGbot-LLM-RAG
```

### 2. Настройка окружения

#### Windows (PowerShell) - Рекомендуется:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### Linux/macOS:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Настройка переменных окружения

Создайте файл `.env`:
```env
# Обязательные
TELEGRAM_TOKEN=your_telegram_token_here
HUGGINGFACEHUB_API_TOKEN=your_hf_token_here

# Настройки базы данных (если используется)
DATABASE_URI=sqlite:///./sql_app.db

# Настройки ChromaDB
CHROMA_DB_PATH=./chroma_db

# Настройки модели (опционально)
MODEL_NAME=Qwen/Qwen2-1.5B-Instruct
DEVICE=cpu
INFERENCE_BACKEND=cpu

# Отключение телеметрии
ANONYMIZED_TELEMETRY=false
```

### 4. Запуск бота

#### 🚀 Простой запуск (рекомендуется):
```powershell
.\start_cpu_optimized.ps1
```

Скрипт автоматически:
- ✅ Активирует виртуальное окружение
- ✅ Проверяет Python
- ✅ Устанавливает CPU-оптимизированные настройки
- ✅ Загружает модель Qwen2-1.5B-Instruct
- ✅ Инициализирует векторную базу знаний
- ✅ Запускает бота

#### 📊 Мониторинг запуска:
```powershell
.\monitor_bot.ps1
```

Показывает:
- ⏳ Процесс загрузки модели
- ✅ Статус инициализации
- 🎉 Готовность к работе

#### 🔧 Ручной запуск:

```powershell
# Активация окружения
.venv\Scripts\Activate.ps1

# CPU-оптимизированный режим
$env:INFERENCE_BACKEND="cpu"
$env:DEVICE="cpu"
$env:MODEL_NAME="Qwen/Qwen2-1.5B-Instruct"
$env:MODEL_MAX_LENGTH="512"
$env:MODEL_TEMPERATURE="0.7"
$env:OMP_NUM_THREADS="4"
$env:MKL_NUM_THREADS="4"
$env:OPENBLAS_NUM_THREADS="4"
$env:PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:128"
$env:TOKENIZERS_PARALLELISM="false"
$env:PYTHONUNBUFFERED="1"
$env:ANONYMIZED_TELEMETRY="false"
python .\bot.py
```

## ⚙️ CPU Оптимизации

### 📊 Производительность (тестировано на Qwen2-1.5B-Instruct)

| Параметр | Значение | Описание |
|----------|----------|----------|
| **Инициализация** | ~5-7 секунд | Загрузка модели и векторной БД |
| **Время ответа** | ~13-15 секунд | Обработка запроса и генерация |
| **Память** | ~4-6 GB RAM | Потребление оперативной памяти |
| **CPU потоки** | 4 потока | Оптимизировано для производительности |

### 🔧 Применяемые оптимизации:

#### **Модель:**
- ✅ Оптимизированная модель Qwen2-1.5B-Instruct
- ✅ torch.float32 для стабильности на CPU
- ✅ Отключен быстрый токенизатор (use_fast=False)
- ✅ model.eval() для режима инференса

#### **Генерация:**
- ✅ max_new_tokens=512 для качественных ответов
- ✅ temperature=0.7 для баланса креативности/точности
- ✅ return_full_text=False для экономии памяти
- ✅ do_sample=True с top_p=0.9

#### **CPU/Память:**
- ✅ OMP_NUM_THREADS=4 (оптимальные потоки)
- ✅ MKL_NUM_THREADS=4 (Intel Math Kernel)
- ✅ OPENBLAS_NUM_THREADS=4 (OpenBLAS)
- ✅ PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
- ✅ TOKENIZERS_PARALLELISM=false

#### **RAG:**
- ✅ Similarity search вместо MMR
- ✅ k=2 документа для фокусированного контекста
- ✅ Упрощенный промпт шаблон без дублирования

## 📁 Структура проекта

```
LFP-TGbot-LLM_CPU-DS/
├── bot.py                    # Основной файл бота
├── chains.py                 # CPU-оптимизированные LangChain цепи
├── embeddings.py             # Векторное хранилище ChromaDB
├── system_prompt.txt         # Системный промпт (вынесен в корень)
├── start_cpu_optimized.ps1   # CPU-оптимизированный скрипт запуска
├── monitor_bot.ps1           # Скрипт мониторинга загрузки
├── flask_app/                # Flask приложение
│   ├── __init__.py
│   └── models.py             # Модели базы данных
├── knowledge_base/           # База знаний
│   ├── knowledge_base.md     # Основная информация
│   ├── delivery_terms.md     # Условия доставки
│   └── product_catalog.md    # Каталог товаров
├── logs/                     # Логи бота
├── chroma_db/                # Векторная база данных
├── .venv/                    # Виртуальное окружение
├── requirements.txt          # Основные зависимости
├── requirements.lock.txt     # Замороженные версии для воспроизводимости
├── .env                      # Переменные окружения (создать из .env.example)
├── .env.example              # Пример переменных окружения
└── README.md                 # Документация
```

## 🔧 Конфигурация

### Модели
- **LLM**: Qwen2-1.5B-Instruct (CPU-оптимизированная)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector Store**: ChromaDB

### Устройство
- **CPU**: Единственный поддерживаемый режим (PyTorch с оптимизациями)

### Файлы конфигурации

#### `.env` - основные переменные окружения:
```env
TELEGRAM_TOKEN=your_bot_token_here
HUGGINGFACEHUB_API_TOKEN=your_hf_token_here
MODEL_NAME=Qwen/Qwen2-1.5B-Instruct
DEVICE=cpu
INFERENCE_BACKEND=cpu
MODEL_MAX_LENGTH=512
MODEL_TEMPERATURE=0.7
ANONYMIZED_TELEMETRY=false
```

#### `requirements.txt` vs `requirements.lock.txt`:
- **`requirements.txt`** - основные зависимости с минимальными версиями
- **`requirements.lock.txt`** - точные версии всех пакетов для воспроизводимой установки

**Рекомендация:** Используйте `requirements.lock.txt` для стабильной установки:
```powershell
pip install -r requirements.lock.txt
```

## 📊 Мониторинг

### Логи
- Файл: `logs/bot.log`
- Уровень: INFO
- Формат: Временная метка, уровень, сообщение

### База данных
- **SQLite**: Для разработки (`sql_app.db`)
- **PostgreSQL**: Для продакшена (настройте `DATABASE_URI`)

### Health Check
- Endpoint: `http://localhost:5000/health`
- Статус: 200 OK при работе бота

## 🚨 Устранение неполадок

### Частые проблемы:

1. **Ошибка импорта модулей**
   ```powershell
   pip install -r requirements.lock.txt
   ```

2. **Недостаточно памяти**
   - Закройте другие приложения
   - Перезапустите бота

3. **Ошибки Telegram API**
   - Проверьте `TELEGRAM_TOKEN` в `.env`
   - Убедитесь в правах бота

4. **Проблемы с ChromaDB**
   ```powershell
   # Удалите старую базу и перезапустите
   Remove-Item -Recurse -Force chroma_db
   .\start_cpu_optimized.ps1
   ```

5. **Ошибки стартового скрипта**
   ```powershell
   # Проверьте политику выполнения
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\start_cpu_optimized.ps1
   ```

6. **Медленная работа**
   - Проверьте загрузку CPU (должна быть 80-100% во время генерации)
   - Убедитесь, что используются правильные переменные окружения
   - Закройте ненужные приложения

### 🔍 Диагностика

**Проверка окружения:**
```powershell
python -c "import telegram, flask, langchain, transformers; print('✅ Все модули найдены')"
```

**Проверка переменных:**
```powershell
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('TELEGRAM_TOKEN:', '✅ OK' if os.getenv('TELEGRAM_TOKEN') else '❌ MISSING')"
```

**Проверка модели:**
```powershell
python -c "from transformers import AutoTokenizer; t = AutoTokenizer.from_pretrained('Qwen/Qwen2-1.5B-Instruct'); print('✅ Модель доступна')"
```

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте ветку для фичи
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE)

## 📞 Поддержка

- Issues: [GitHub Issues](https://github.com/yourusername/LFP-TGbot-LLM-RAG/issues)
- Email: support@example.com
