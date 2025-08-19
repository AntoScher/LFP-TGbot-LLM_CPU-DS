# Простой мониторинг загрузки модели

Write-Host "🔍 МОНИТОРИНГ ЗАГРУЗКИ МОДЕЛИ" -ForegroundColor Cyan
Write-Host "=" * 40 -ForegroundColor Cyan

while ($true) {
    Clear-Host
    Write-Host "🔍 МОНИТОРИНГ ЗАГРУЗКИ МОДЕЛИ" -ForegroundColor Cyan
    Write-Host "=" * 40 -ForegroundColor Cyan
    Write-Host "Время: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Yellow
    
    # Проверяем процесс Python
    $pythonProcess = Get-Process python -ErrorAction SilentlyContinue
    if ($pythonProcess) {
        Write-Host "✅ Процесс Python запущен (PID: $($pythonProcess.Id))" -ForegroundColor Green
    } else {
        Write-Host "❌ Процесс Python не найден" -ForegroundColor Red
        break
    }
    
    # Проверяем лог файл
    if (Test-Path "logs\bot.log") {
        Write-Host "📄 Лог файл найден" -ForegroundColor Green
        
        # Последние записи лога
        $lastLogs = Get-Content "logs\bot.log" -Tail 3
        Write-Host "📋 Последние записи лога:" -ForegroundColor Yellow
        foreach ($log in $lastLogs) {
            Write-Host "   $log" -ForegroundColor Gray
        }
        
        # Проверяем ключевые сообщения
        $logContent = Get-Content "logs\bot.log" -Raw
        if ($logContent -match "QA chain initialized successfully") {
            Write-Host "🎉 МОДЕЛЬ ЗАГРУЖЕНА И БОТ ГОТОВ К РАБОТЕ!" -ForegroundColor Green
            Write-Host "✅ Бот полностью инициализирован" -ForegroundColor Green
            break
        }
        elseif ($logContent -match "Application started") {
            Write-Host "🚀 Приложение запущено, модель загружается..." -ForegroundColor Yellow
        }
        elseif ($logContent -match "Initializing QA chain") {
            Write-Host "⏳ Инициализация QA цепочки..." -ForegroundColor Yellow
        }
        elseif ($logContent -match "Loading model") {
            Write-Host "📥 Загрузка модели..." -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Лог файл не найден" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "⏳ Ожидание 5 секунд..." -ForegroundColor Gray
    Start-Sleep -Seconds 5
}

Write-Host ""
Write-Host "🎯 МОНИТОРИНГ ЗАВЕРШЕН" -ForegroundColor Green
Write-Host "Бот готов к работе!" -ForegroundColor Green
