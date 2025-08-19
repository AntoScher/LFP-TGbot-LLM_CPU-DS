# Скрипт запуска усовершенствованного бота с кнопками и DeepSeek
# Автор: AI Assistant
# Дата: 2025-08-19

Write-Host "🚀 Запуск усовершенствованного бота с кнопками и DeepSeek..." -ForegroundColor Green

# Проверяем наличие виртуального окружения
if (-not (Test-Path ".venv")) {
    Write-Host "❌ Виртуальное окружение не найдено!" -ForegroundColor Red
    Write-Host "Создайте виртуальное окружение: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# Активируем виртуальное окружение
Write-Host "📦 Активация виртуального окружения..." -ForegroundColor Cyan
try {
    & ".venv\Scripts\Activate.ps1"
    Write-Host "✅ Виртуальное окружение активировано" -ForegroundColor Green
} catch {
    Write-Host "❌ Ошибка активации виртуального окружения: $_" -ForegroundColor Red
    exit 1
}

# Оптимизированные настройки для CPU
Write-Host "[INFO] Setting CPU optimized environment..." -ForegroundColor Cyan

# Основные настройки
$env:INFERENCE_BACKEND = "cpu"
$env:DEVICE = "cpu"
$env:PYTHONUNBUFFERED = "1"
$env:ANONYMIZED_TELEMETRY = "false"

# Оптимизация PyTorch для CPU
$env:OMP_NUM_THREADS = "4"  # Ограничиваем количество потоков
$env:MKL_NUM_THREADS = "4"
$env:OPENBLAS_NUM_THREADS = "4"

# Оптимизация модели
$env:MODEL_NAME = "Qwen/Qwen2-1.5B-Instruct"  # Модель
$env:MODEL_MAX_LENGTH = "512"  # Увеличиваем длину генерации для лучших ответов
$env:MODEL_TEMPERATURE = "0.7"  # Возвращаем к стандартной температуре

# Оптимизация памяти
$env:PYTORCH_CUDA_ALLOC_CONF = "max_split_size_mb:128"
$env:TOKENIZERS_PARALLELISM = "false"

# Проверяем наличие .env файла
if (-not (Test-Path ".env")) {
    Write-Host "❌ Файл .env не найден!" -ForegroundColor Red
    Write-Host "Создайте файл .env с необходимыми переменными окружения" -ForegroundColor Yellow
    exit 1
}

# Проверяем наличие необходимых файлов
$requiredFiles = @(
    "bot_enhanced.py",
    "deepseek_client.py", 
    "database.py",
    "button_handlers.py",
    "chains.py",
    "embeddings.py",
    "system_prompt.txt"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "❌ Файл $file не найден!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ Все необходимые файлы найдены" -ForegroundColor Green

# Проверяем зависимости
Write-Host "🔍 Проверка зависимостей..." -ForegroundColor Cyan
try {
    python -c "import requests, sqlite3, aiogram, langchain, transformers, torch" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Не все зависимости установлены!" -ForegroundColor Red
        Write-Host "Установите зависимости: pip install -r requirements.lock.txt" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "✅ Зависимости проверены" -ForegroundColor Green
} catch {
    Write-Host "❌ Ошибка проверки зависимостей: $_" -ForegroundColor Red
    exit 1
}

# Запускаем бота
Write-Host "🤖 Запуск усовершенствованного бота..." -ForegroundColor Green
Write-Host "📋 Функции:" -ForegroundColor Cyan
Write-Host "   • Интерактивные кнопки" -ForegroundColor White
Write-Host "   • Режим 'О компании' (RAG)" -ForegroundColor White
Write-Host "   • Режим 'Общие вопросы' (DeepSeek)" -ForegroundColor White
Write-Host "   • История разговоров в SQLite" -ForegroundColor White
Write-Host "   • Обработка ошибок API" -ForegroundColor White
Write-Host ""

try {
    python bot_enhanced.py
} catch {
    Write-Host "❌ Ошибка запуска бота: $_" -ForegroundColor Red
    Write-Host "Проверьте логи в файле logs/bot_enhanced.log" -ForegroundColor Yellow
    exit 1
}
