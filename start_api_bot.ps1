# Скрипт запуска API бота
# Автор: AI Assistant
# Дата: 2025-08-19

Write-Host "❓ Запуск API бота..." -ForegroundColor Green

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
    "bot_api_only.py",
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

# Проверяем, что бот не запущен
$pythonProcesses = Get-Process | Where-Object {$_.ProcessName -like "*python*"}
if ($pythonProcesses) {
    Write-Host "⚠️ Обнаружены запущенные процессы Python. Останавливаю..." -ForegroundColor Yellow
    $pythonProcesses | Stop-Process -Force
    Start-Sleep -Seconds 2
}

# Запускаем API бот
Write-Host "[INFO] Запуск API бота..." -ForegroundColor Cyan
Write-Host "📝 Логи будут сохранены в: logs/bot_api_only.log" -ForegroundColor Cyan
Write-Host "🔍 Для мониторинга используйте: .\monitor_api_bot.ps1" -ForegroundColor Cyan
Write-Host "⏹️ Для остановки нажмите Ctrl+C" -ForegroundColor Cyan
Write-Host ""

try {
    python bot_api_only.py
} catch {
    Write-Host "❌ Ошибка запуска бота: $_" -ForegroundColor Red
    exit 1
}
