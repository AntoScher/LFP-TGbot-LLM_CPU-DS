# Оптимизированный скрипт для запуска LFP-TGbot-LLM-RAG в CPU режиме
# С улучшенными настройками производительности

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

Write-Host "==============================" -ForegroundColor Green
Write-Host " LFP-TGbot-LLM-RAG CPU Optimized" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green

# Активируем виртуальное окружение
Write-Host "[INFO] Activating venv..." -ForegroundColor Cyan
& ".venv\Scripts\Activate.ps1"

# Проверяем Python
Write-Host "[INFO] Checking Python..." -ForegroundColor Cyan
$pythonVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
if ($pythonVersion) {
    Write-Host "[OK  ] Python version: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "[ERR ] Python not found" -ForegroundColor Red
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

# Оптимизация модели (оставляем Qwen2-1.5B-Instruct)
$env:MODEL_NAME = "Qwen/Qwen2-1.5B-Instruct"  # Оставляем текущую модель
$env:MODEL_MAX_LENGTH = "512"  # Увеличиваем длину генерации для лучших ответов
$env:MODEL_TEMPERATURE = "0.7"  # Стандартная температура

# Оптимизация памяти
$env:PYTORCH_CUDA_ALLOC_CONF = "max_split_size_mb:128"
$env:TOKENIZERS_PARALLELISM = "false"

Write-Host "[INFO] CPU Optimizations:" -ForegroundColor Yellow
Write-Host "  - Model: Qwen2-1.5B-Instruct (оптимизированные настройки)" -ForegroundColor White
Write-Host "  - Max tokens: 512 (улучшенные ответы)" -ForegroundColor White
Write-Host "  - Temperature: 0.7 (стандартная)" -ForegroundColor White
Write-Host "  - Threads: 4 (оптимизировано для CPU)" -ForegroundColor White
Write-Host "  - Fixed: System prompt duplication" -ForegroundColor Green
Write-Host "  - Fixed: Optimized retriever settings" -ForegroundColor Green

Write-Host ""
Write-Host "[INFO] Starting bot with CPU optimizations..." -ForegroundColor Cyan
python .\bot.py
