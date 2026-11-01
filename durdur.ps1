# Antigravity Voice Typing - Durdurucu Betik
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "SilentlyContinue"

$currentDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $currentDir) { $currentDir = Get-Location }

$killed = 0
$pidFile = Join-Path $currentDir "app.pid"
$filePid = $null
if (Test-Path $pidFile) {
    try {
        $filePid = [int]((Get-Content $pidFile -Raw).Trim())
    } catch {}
}

# Strict process isolation: SADECE Antigravity Voice Typing sureclerini hedefle
$procs = Get-CimInstance Win32_Process | Where-Object {
    ($_.Name -like "python*" -or $_.Name -like "pythonw*") -and (
        $_.CommandLine -like "*ANTIGR~1*app.py*" -or
        $_.CommandLine -like "*Antigravity-Voice-Typing*app.py*" -or
        $_.CommandLine -like "*Antigravity-Voice-Typing*" -or
        ($filePid -ne $null -and $_.ProcessId -eq $filePid -and ($_.CommandLine -like "*app.py*" -or $_.CommandLine -like "*Voice*"))
    )
}

if ($procs) {
    foreach ($p in $procs) {
        try {
            Stop-Process -Id $p.ProcessId -Force -ErrorAction Stop
            Write-Host ("[DURDURULDU] PID: {0} ({1})" -f $p.ProcessId, $p.Name) -ForegroundColor Green
            $killed++
        } catch {
            Write-Host ("[UYARI] PID {0} durdurulamadi: {1}" -f $p.ProcessId, $_.Exception.Message) -ForegroundColor Yellow
        }
    }
}

if (Test-Path $pidFile) {
    Remove-Item -Force $pidFile -ErrorAction SilentlyContinue
    Write-Host "[TEMIZLENDI] app.pid dosyasi kaldirildi." -ForegroundColor Gray
}

if ($killed -eq 0) {
    Write-Host "[BILGI] Calisan bir Voice Typing sureci bulunamadi." -ForegroundColor Cyan
} else {
    Write-Host ("[BASARILI] Toplam {0} surec temizce sonlandirildi." -f $killed) -ForegroundColor Green
}
