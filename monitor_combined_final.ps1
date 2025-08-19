# Скрипт мониторинга финального объединенного бота
# Автор: AI Assistant
# Дата: 2025-08-19

Write-Host "🔍 Мониторинг финального объединенного бота..." -ForegroundColor Cyan

# Проверяем, запущен ли бот
$botProcess = Get-Process | Where-Object {$_.ProcessName -like "*python*" -and $_.CommandLine -like "*bot_combined_final.py*"}
if ($botProcess) {
    Write-Host "✅ Финальный бот запущен (PID: $($botProcess.Id))" -ForegroundColor Green
} else {
    Write-Host "❌ Финальный бот НЕ запущен!" -ForegroundColor Red
    Write-Host "Запустите бот командой: .\start_combined_final.ps1" -ForegroundColor Yellow
    exit 1
}

# Проверяем файлы логов
$logFile = "logs/bot_combined_final.log"
if (Test-Path $logFile) {
    Write-Host "✅ Файл логов найден: $logFile" -ForegroundColor Green
} else {
    Write-Host "⚠️ Файл логов не найден: $logFile" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📊 Статистика использования ресурсов:" -ForegroundColor Cyan

# Мониторинг в реальном времени
while ($true) {
    Clear-Host
    Write-Host "🔍 Мониторинг финального бота - $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Cyan
    Write-Host "🎯 Режимы: 🏢 RAG (О компании) + ❓ DeepSeek API (Общие вопросы)" -ForegroundColor White
    Write-Host "=" * 70 -ForegroundColor Gray
    
    # Проверяем процесс бота
    $botProcess = Get-Process | Where-Object {$_.ProcessName -like "*python*" -and $_.CommandLine -like "*bot_combined_final.py*"}
    if ($botProcess) {
        Write-Host "✅ Финальный бот активен (PID: $($botProcess.Id))" -ForegroundColor Green
        
        # Показываем использование памяти и CPU
        $memoryMB = [math]::Round($botProcess.WorkingSet64 / 1MB, 2)
        $cpuPercent = [math]::Round($botProcess.CPU, 2)
        Write-Host "💾 Память: $memoryMB MB" -ForegroundColor White
        Write-Host "⚡ CPU: $cpuPercent%" -ForegroundColor White
    } else {
        Write-Host "❌ Финальный бот остановлен!" -ForegroundColor Red
        break
    }
    
    # Показываем последние записи из лога
    if (Test-Path $logFile) {
        Write-Host ""
        Write-Host "📝 Последние записи из лога:" -ForegroundColor Cyan
        try {
            $lastLines = Get-Content $logFile -Tail 5 -ErrorAction SilentlyContinue
            foreach ($line in $lastLines) {
                if ($line -match "ERROR") {
                    Write-Host $line -ForegroundColor Red
                } elseif ($line -match "WARNING") {
                    Write-Host $line -ForegroundColor Yellow
                } elseif ($line -match "INFO") {
                    Write-Host $line -ForegroundColor Green
                } else {
                    Write-Host $line -ForegroundColor White
                }
            }
        } catch {
            Write-Host "⚠️ Не удалось прочитать лог: $_" -ForegroundColor Yellow
        }
    }
    
    # Показываем размер файлов
    Write-Host ""
    Write-Host "📁 Размеры файлов:" -ForegroundColor Cyan
    
    if (Test-Path $logFile) {
        $logSize = (Get-Item $logFile).Length
        Write-Host "📝 Лог: $([math]::Round($logSize/1KB, 2)) KB" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "🎯 Функциональность бота:" -ForegroundColor Cyan
    Write-Host "   🏢 RAG режим - база знаний о компании" -ForegroundColor White
    Write-Host "   ❓ DeepSeek API - ИИ-помощник для общих вопросов" -ForegroundColor White
    Write-Host ""
    Write-Host "⏹️ Для остановки мониторинга нажмите Ctrl+C" -ForegroundColor Yellow
    Write-Host "🔄 Обновление через 5 секунд..." -ForegroundColor Gray
    
    Start-Sleep -Seconds 5
}
