# Скрипт запуска LangChain RAG бота
# Автор: AI Assistant
# Дата: 2025-08-19

Write-Host "🧠 Запуск LangChain RAG бота..." -ForegroundColor Green

# Проверяем, активировано ли правильное виртуальное окружение
if ($env:VIRTUAL_ENV -and $env:VIRTUAL_ENV.Contains("venv_langchain")) {
    Write-Host "✅ LangChain окружение уже активировано" -ForegroundColor Green
} else {
    Write-Host "⚠️ Активирую LangChain виртуальное окружение..." -ForegroundColor Yellow
    & ".\.venv_langchain\Scripts\Activate.ps1"
}

# Оптимизированные настройки для CPU
Write-Host "[INFO] Setting CPU optimized environment for LangChain..." -ForegroundColor Cyan

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
    "bot_langchain_rag.py",
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

# Проверяем, что другие боты не запущены
$pythonProcesses = Get-Process | Where-Object {$_.ProcessName -like "*python*"}
if ($pythonProcesses) {
    Write-Host "⚠️ Обнаружены запущенные процессы Python. Останавливаю..." -ForegroundColor Yellow
    $pythonProcesses | Stop-Process -Force
    Start-Sleep -Seconds 2
}

# Запускаем LangChain RAG бот
Write-Host "[INFO] Запуск LangChain RAG бота..." -ForegroundColor Cyan
Write-Host "📝 Логи будут сохранены в: logs/bot_langchain_rag.log" -ForegroundColor Cyan
Write-Host "🔍 Для мониторинга используйте: .\monitor_langchain_rag.ps1" -ForegroundColor Cyan
Write-Host "⏹️ Для остановки нажмите Ctrl+C" -ForegroundColor Cyan
Write-Host ""
Write-Host "🧠 Функциональность:" -ForegroundColor Cyan
Write-Host "   🔍 Настоящий векторный поиск" -ForegroundColor White
Write-Host "   🧠 LangChain QA цепи" -ForegroundColor White
Write-Host "   📚 Семантический анализ документов" -ForegroundColor White
Write-Host ""

try {
    python bot_langchain_rag.py
} catch {
    Write-Host "❌ Ошибка запуска бота: $_" -ForegroundColor Red
    exit 1
}
