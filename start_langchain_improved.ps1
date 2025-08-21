# Скрипт запуска улучшенного LangChain RAG бота
# Автор: AI Assistant
# Дата: 2025-08-21

Write-Host "🧠 Запуск УЛУЧШЕННОГО LangChain RAG бота..." -ForegroundColor Green

# Активируем LangChain виртуальное окружение
Write-Host "⚠️ Активирую LangChain виртуальное окружение..." -ForegroundColor Yellow
if (Test-Path ".\.venv_langchain\Scripts\Activate.ps1") {
    & ".\.venv_langchain\Scripts\Activate.ps1"
    Write-Host "✅ LangChain окружение активировано" -ForegroundColor Green
} else {
    Write-Host "❌ LangChain окружение не найдено!" -ForegroundColor Red
    exit 1
}

# CPU оптимизации для LangChain
Write-Host "[INFO] Setting CPU optimized environment for improved LangChain..." -ForegroundColor Cyan

$env:INFERENCE_BACKEND = "cpu"
$env:DEVICE = "cpu"
$env:MODEL_NAME = "Qwen/Qwen2-1.5B-Instruct"
$env:MODEL_MAX_LENGTH = "256"  # Уменьшено для скорости
$env:MODEL_TEMPERATURE = "0.3"  # Меньше галлюцинаций
$env:OMP_NUM_THREADS = "4"
$env:MKL_NUM_THREADS = "4"
$env:OPENBLAS_NUM_THREADS = "4"
$env:PYTORCH_CUDA_ALLOC_CONF = "max_split_size_mb:64"  # Меньше памяти
$env:TOKENIZERS_PARALLELISM = "false"
$env:PYTHONUNBUFFERED = "1"
$env:ANONYMIZED_TELEMETRY = "false"

Write-Host "[INFO] Environment variables set successfully" -ForegroundColor Green

# Проверяем наличие необходимых файлов
$requiredFiles = @(
    "bot_langchain_improved.py",
    "chains_improved.py",
    "embeddings.py",
    ".env",
    "system_prompt_improved.txt"
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
    Write-Host "⚠️ Останавливаю другие Python процессы..." -ForegroundColor Yellow
    $pythonProcesses | Stop-Process -Force
    Start-Sleep -Seconds 2
}

# Запускаем улучшенный LangChain RAG бот
Write-Host "[INFO] Запуск улучшенного LangChain RAG бота..." -ForegroundColor Cyan
Write-Host "📝 Логи будут сохранены в: logs/bot_langchain_improved.log" -ForegroundColor Cyan
Write-Host "🔍 Для мониторинга используйте: Get-Content logs/bot_langchain_improved.log -Tail 10" -ForegroundColor Cyan
Write-Host "⏹️ Для остановки нажмите Ctrl+C" -ForegroundColor Cyan
Write-Host ""
Write-Host "🧠 Улучшения:" -ForegroundColor Cyan
Write-Host "   ⚡ Оптимизированная скорость (256 токенов)" -ForegroundColor White
Write-Host "   🎯 Улучшенная точность (temperature=0.3)" -ForegroundColor White
Write-Host "   🛡️ Защита от галлюцинаций" -ForegroundColor White
Write-Host "   💾 Меньше потребление памяти" -ForegroundColor White
Write-Host ""

try {
    python bot_langchain_improved.py
} catch {
    Write-Host "❌ Ошибка запуска улучшенного бота: $_" -ForegroundColor Red
    exit 1
}
