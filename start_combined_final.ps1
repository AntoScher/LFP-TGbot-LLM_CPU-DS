# Скрипт запуска финального объединенного бота
# Автор: AI Assistant
# Дата: 2025-08-19

Write-Host "🚀 Запуск финального объединенного бота (RAG + DeepSeek API)..." -ForegroundColor Green

# Проверяем, активировано ли виртуальное окружение
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️ Виртуальное окружение не активировано. Активирую..." -ForegroundColor Yellow
    & ".\.venv\Scripts\Activate.ps1"
}

# Основные настройки
Write-Host "[INFO] Setting environment..." -ForegroundColor Cyan

$env:PYTHONUNBUFFERED = "1"
$env:ANONYMIZED_TELEMETRY = "false"

Write-Host "[INFO] Environment variables set successfully" -ForegroundColor Green

# Проверяем наличие необходимых файлов
$requiredFiles = @(
    "bot_combined_final.py",
    ".env"
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

# Запускаем финальный объединенный бот
Write-Host "[INFO] Запуск финального объединенного бота..." -ForegroundColor Cyan
Write-Host "📝 Логи будут сохранены в: logs/bot_combined_final.log" -ForegroundColor Cyan
Write-Host "🔍 Для мониторинга используйте: .\monitor_combined_final.ps1" -ForegroundColor Cyan
Write-Host "⏹️ Для остановки нажмите Ctrl+C" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎯 Функциональность:" -ForegroundColor Cyan
Write-Host "   🏢 RAG режим - вопросы о компании" -ForegroundColor White
Write-Host "   ❓ DeepSeek режим - общие вопросы" -ForegroundColor White
Write-Host ""

try {
    python bot_combined_final.py
} catch {
    Write-Host "❌ Ошибка запуска бота: $_" -ForegroundColor Red
    exit 1
}
