# Скрипт мониторинга усовершенствованного бота
# Автор: AI Assistant
# Дата: 2025-08-19

Write-Host "🔍 Мониторинг усовершенствованного бота..." -ForegroundColor Green

$botProcess = $null
$logFile = "logs/bot_enhanced.log"
$dbFile = "bot_history.db"

# Функция для проверки статуса бота
function Test-BotStatus {
    $processes = Get-Process -Name "python" -ErrorAction SilentlyContinue
    foreach ($process in $processes) {
        try {
            $commandLine = (Get-WmiObject -Class Win32_Process -Filter "ProcessId = $($process.Id)").CommandLine
            if ($commandLine -and $commandLine.Contains("bot_enhanced.py")) {
                return $process
            }
        } catch {
            # Игнорируем ошибки доступа
        }
    }
    return $null
}

# Функция для проверки логов
function Test-LogFile {
    if (Test-Path $logFile) {
        $lastModified = (Get-Item $logFile).LastWriteTime
        $timeSinceModified = (Get-Date) - $lastModified
        
        if ($timeSinceModified.TotalMinutes -lt 2) {
            Write-Host "✅ Лог файл обновляется (последнее обновление: $($lastModified.ToString('HH:mm:ss')))" -ForegroundColor Green
            return $true
        } else {
            Write-Host "⚠️ Лог файл не обновлялся более 2 минут (последнее обновление: $($lastModified.ToString('HH:mm:ss')))" -ForegroundColor Yellow
            return $false
        }
    } else {
        Write-Host "❌ Лог файл не найден" -ForegroundColor Red
        return $false
    }
}

# Функция для проверки базы данных
function Test-Database {
    if (Test-Path $dbFile) {
        $dbSize = (Get-Item $dbFile).Length
        Write-Host "📊 База данных: $($dbSize) байт" -ForegroundColor Cyan
        return $true
    } else {
        Write-Host "❌ База данных не найдена" -ForegroundColor Red
        return $false
    }
}

# Функция для отображения последних логов
function Show-RecentLogs {
    if (Test-Path $logFile) {
        Write-Host "📋 Последние записи лога:" -ForegroundColor Cyan
        try {
            $recentLogs = Get-Content $logFile -Tail 10 -ErrorAction SilentlyContinue
            foreach ($log in $recentLogs) {
                if ($log -match "ERROR") {
                    Write-Host "  ❌ $log" -ForegroundColor Red
                } elseif ($log -match "WARNING") {
                    Write-Host "  ⚠️ $log" -ForegroundColor Yellow
                } elseif ($log -match "INFO") {
                    Write-Host "  ℹ️ $log" -ForegroundColor White
                } else {
                    Write-Host "  📝 $log" -ForegroundColor Gray
                }
            }
        } catch {
            Write-Host "  ❌ Ошибка чтения лога: $_" -ForegroundColor Red
        }
    }
}

# Основной цикл мониторинга
while ($true) {
    Clear-Host
    Write-Host "🤖 МОНИТОРИНГ УСОВЕРШЕНСТВОВАННОГО БОТА" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Gray
    Write-Host "Время: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
    Write-Host ""
    
    # Проверяем процесс бота
    $botProcess = Test-BotStatus
    if ($botProcess) {
        Write-Host "✅ Бот запущен (PID: $($botProcess.Id))" -ForegroundColor Green
        Write-Host "   Время работы: $((Get-Date) - $botProcess.StartTime)" -ForegroundColor White
        Write-Host "   Использование CPU: $([math]::Round($botProcess.CPU, 2))%" -ForegroundColor White
        Write-Host "   Использование памяти: $([math]::Round($botProcess.WorkingSet64 / 1MB, 2)) MB" -ForegroundColor White
    } else {
        Write-Host "❌ Бот не запущен!" -ForegroundColor Red
        Write-Host "   Запустите бота: .\start_enhanced.ps1" -ForegroundColor Yellow
    }
    
    Write-Host ""
    
    # Проверяем лог файл
    $logStatus = Test-LogFile
    
    Write-Host ""
    
    # Проверяем базу данных
    $dbStatus = Test-Database
    
    Write-Host ""
    
    # Показываем последние логи
    Show-RecentLogs
    
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Gray
    Write-Host "Нажмите Ctrl+C для выхода" -ForegroundColor Yellow
    Write-Host "Обновление через 10 секунд..." -ForegroundColor Gray
    
    Start-Sleep -Seconds 10
}
