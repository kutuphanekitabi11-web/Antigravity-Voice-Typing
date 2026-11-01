# Antigravity Voice Typing - Baslatici Betik
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "SilentlyContinue"

$currentDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $currentDir) { $currentDir = Get-Location }

# Resolve 8.3 short path for app.py to prevent Turkish cp1254 codec errors and ensure process isolation
$appScript = Join-Path $currentDir "app.py"
try {
    $fso = New-Object -ComObject Scripting.FileSystemObject
    if (Test-Path $appScript) {
        $shortApp = $fso.GetFile($appScript).ShortPath
        if ($shortApp) { $appScript = $shortApp }
    }
} catch {}

$pidFile = Join-Path $currentDir "app.pid"
$filePid = $null
if (Test-Path $pidFile) {
    try {
        $filePid = [int]((Get-Content $pidFile -Raw).Trim())
    } catch {}
}

# Strict process query: Must be Voice Typing app.py (never touch Okul-Antigravity or unrelated app.py)
$procs = Get-CimInstance Win32_Process | Where-Object {
    ($_.Name -like "python*" -or $_.Name -like "pythonw*") -and (
        $_.CommandLine -like "*ANTIGR~1*app.py*" -or
        $_.CommandLine -like "*Antigravity-Voice-Typing*app.py*" -or
        ($filePid -ne $null -and $_.ProcessId -eq $filePid -and ($_.CommandLine -like "*app.py*" -or $_.CommandLine -like "*Voice*"))
    )
}

if ($procs) {
    $existingPids = ($procs | Select-Object -ExpandProperty ProcessId) -join ", "
    Write-Host ("[UYARI] Antigravity Voice Typing zaten calisiyor! (PID: {0})" -f $existingPids) -ForegroundColor Yellow
    Write-Host "Yeniden baslatmak icin once 'durdur.bat' calistiriniz."
    exit 0
}

Write-Host "[BILGI] Antigravity Voice Typing arka planda baslatiliyor..." -ForegroundColor Cyan

# pythonw.exe ile app.py calistir (8.3 izole yol ile)
$startInfo = New-Object System.Diagnostics.ProcessStartInfo
$startInfo.FileName = "pythonw.exe"
$startInfo.Arguments = "`"$appScript`""
$startInfo.WorkingDirectory = $currentDir
$startInfo.UseShellExecute = $true
$startInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden

try {
    $startedProc = [System.Diagnostics.Process]::Start($startInfo)
    Start-Sleep -Milliseconds 900

    # Basladigini dogrula (sadece Antigravity Voice Typing sureci)
    $newProcs = Get-CimInstance Win32_Process | Where-Object {
        ($_.Name -like "python*" -or $_.Name -like "pythonw*") -and (
            $_.CommandLine -like "*ANTIGR~1*app.py*" -or
            $_.CommandLine -like "*Antigravity-Voice-Typing*app.py*" -or
            ($_.CommandLine -like "*app.py*" -and $_.CommandLine -notlike "*Okul-Antigravity*")
        )
    }

    if ($newProcs) {
        $pids = ($newProcs | Select-Object -ExpandProperty ProcessId) -join ", "
        Write-Host ("[BASARILI] Voice Typing baslatildi! (PID: {0})" -f $pids) -ForegroundColor Green
    } else {
        Write-Host "[BILGI] Baslatma komutu gonderildi." -ForegroundColor Cyan
    }
} catch {
    Write-Host ("[HATA] Baslatilamadi: {0}" -f $_.Exception.Message) -ForegroundColor Red
    exit 1
}
