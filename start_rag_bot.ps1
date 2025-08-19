# Скрипт запуска RAG бота
# Автор: AI Assistant
# Дата: 2025-08-19

Write-Host "🏢 Запуск RAG бота..." -ForegroundColor Green

# Проверяем, активировано ли виртуальное окружение
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️ Виртуальное окружение не активировано. Активирую..." -ForegroundColor Yellow
    & ".\.venv\Scripts\Activate.ps1"
}

# Оптимизированные настройки для CPU
Write-Host "[INFO] Setting CPU optimized environment..." -ForegroundColor Cyan

# Основные настройки
$env:INFERENCE_BACKEND = "cpu"
$env:DEVICE = "cpu"
$env:PYTHONUNBUFFERED = "1"
$env:ANONYMIZED_TELEMETRY = "false"

# Оптимизация PyTorch для CPU
$env:OMP_NUM_THREADS = "4"
$env:MKL_NUM_THREADS = "4"
$env:OPENBLAS_NUM_THREADS = "4"

# Оптимизация модели
$env:MODEL_NAME = "Qwen/Qwen2-1.5B-Instruct"
$env:MODEL_MAX_LENGTH = "512"
$env:MODEL_TEMPERATURE = "0.7"

# Оптимизация памяти
$env:PYTORCH_CUDA_ALLOC_CONF = "max_split_size_mb:128"
$env:TOKENIZERS_PARALLELISM = "false"

Write-Host "[INFO] Environment variables set successfully" -ForegroundColor Green

# Проверяем наличие необходимых файлов
$requiredFiles = @(
    "bot_rag_only.py",
    "chains.py", 
    "embeddings.py",
    ".env",
    "system_prompt.txt"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file найден" -ForegroundColor Green
    } else {
        Write-Host "❌ $file НЕ НАЙДЕН!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "[INFO] Все необходимые файлы найдены" -ForegroundColor Green

# Проверяем, что бот не запущен
$pythonProcesses = Get-Process | Where-Object {$_.ProcessName -like "*python*"}
if ($pythonProcesses) {
    Write-Host "⚠️ Обнаружены запущенные процессы Python. Останавливаю..." -ForegroundColor Yellow
    $pythonProcesses | Stop-Process -Force
    Start-Sleep -Seconds 2
}

# Запускаем RAG бот
Write-Host "[INFO] Запуск RAG бота..." -ForegroundColor Cyan
Write-Host "📝 Логи будут сохранены в: logs/bot_rag_only.log" -ForegroundColor Cyan
Write-Host "🔍 Для мониторинга используйте: .\monitor_rag_bot.ps1" -ForegroundColor Cyan
Write-Host "⏹️ Для остановки нажмите Ctrl+C" -ForegroundColor Cyan
Write-Host ""

try {
    python bot_rag_only.py
} catch {
    Write-Host "❌ Ошибка запуска бота: $_" -ForegroundColor Red
    exit 1
}
