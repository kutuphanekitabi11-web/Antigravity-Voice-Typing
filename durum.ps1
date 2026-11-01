# Antigravity Voice Typing - Sistem Durum Raporlayici
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "SilentlyContinue"

$currentDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $currentDir) { $currentDir = Get-Location }

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "         [VOICE TYPING] ANTIGRAVITY GLOBAL VOICE TYPING - DURUM         " -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. SUREC KONTROLU
Write-Host "[1] SUREC (PROCESS) DURUMU:" -ForegroundColor Yellow

$pidFile = Join-Path $currentDir "app.pid"
$filePid = $null
if (Test-Path $pidFile) {
    try {
        $filePid = [int]((Get-Content $pidFile -Raw).Trim())
    } catch {}
}

$procs = Get-CimInstance Win32_Process | Where-Object {
    ($_.Name -like "python*" -or $_.Name -like "pythonw*") -and (
        $_.CommandLine -like "*ANTIGR~1*app.py*" -or
        $_.CommandLine -like "*Antigravity-Voice-Typing*app.py*" -or
        $_.CommandLine -like "*Antigravity-Voice-Typing*" -or
        ($filePid -ne $null -and $_.ProcessId -eq $filePid -and ($_.CommandLine -like "*app.py*" -or $_.CommandLine -like "*Voice*"))
    )
}

if ($procs) {
    Write-Host "  * Durum           : " -NoNewline
    Write-Host "AKTIF (CALISIYOR)" -ForegroundColor Green
    
    foreach ($p in $procs) {
        $procObj = Get-Process -Id $p.ProcessId -ErrorAction SilentlyContinue
        $memMb = if ($procObj) { [math]::Round($procObj.WorkingSet64 / 1MB, 2) } else { "N/A" }
        $startTime = if ($procObj) { $procObj.StartTime.ToString("yyyy-MM-dd HH:mm:ss") } else { "N/A" }
        $uptime = if ($procObj) {
            $diff = (Get-Date) - $procObj.StartTime
            "{0:D2}s {1:D2}d {2:D2}sn" -f $diff.Hours, $diff.Minutes, $diff.Seconds
        } else { "N/A" }

        Write-Host "  * PID             : " -NoNewline
        Write-Host "$($p.ProcessId)" -ForegroundColor White
        Write-Host "  * Process Name    : $($p.Name)"
        Write-Host "  * RAM Kullanimi   : $memMb MB"
        Write-Host "  * Baslangic       : $startTime (Calisma Suresi: $uptime)"
        Write-Host "  * Komut Satiri    : $($p.CommandLine)"
    }

    if (Test-Path $pidFile) {
        Write-Host "  * app.pid Dosyasi : Mevcut (Kayitli PID: $filePid)" -ForegroundColor Gray
    } else {
        Write-Host "  * app.pid Dosyasi : Bulunamadi (Surec tespit edildi ancak dosya eksik)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  * Durum           : " -NoNewline
    Write-Host "DURDURULDU (CALISMIYOR)" -ForegroundColor Red
    Write-Host "  * Bilgi           : Arka planda aktif Voice Typing sureci yok."
}

Write-Host ""

# 2. WINDOWS OTOMATIK BASLATMA (STARTUP) KONTROLU
Write-Host "[2] WINDOWS OTOMATIK BASLATMA (STARTUP):" -ForegroundColor Yellow
$startupDir = [System.IO.Path]::Combine($env:APPDATA, "Microsoft\Windows\Start Menu\Programs\Startup")
$vbsPath = Join-Path $startupDir "AntigravityVoiceTyping.vbs"

if (Test-Path $vbsPath) {
    $vbsContent = Get-Content $vbsPath -Raw -ErrorAction SilentlyContinue
    Write-Host "  * Otomatik Baslat : " -NoNewline
    Write-Host "AKTIF (KURULU)" -ForegroundColor Green
    Write-Host "  * Dosya Konumu    : $vbsPath"
    Write-Host "  * Dosya Boyutu    : $((Get-Item $vbsPath).Length) bayt"
    if ($vbsContent -match "baslat\.bat") {
        Write-Host "  * Hedef Tetikleyici: baslat.bat dogrulandi." -ForegroundColor Green
    } else {
        Write-Host "  * Uyari           : VBS dosyasi baslat.bat referansi icermiyor olabilir!" -ForegroundColor Yellow
    }
} else {
    Write-Host "  * Otomatik Baslat : " -NoNewline
    Write-Host "DEVRE DISI (KURULU DEGIL)" -ForegroundColor DarkYellow
    Write-Host "  * Bilgi           : Kurmak icin 'kur_otomatik_baslat.bat' calistiriniz."
}

Write-Host ""

# 3. ANTIGRAVITY MOTOR BAGLANTISI
Write-Host "[3] DIL SUNUCUSU & MOTOR BAGLANTISI:" -ForegroundColor Yellow
$bridgeOutput = & python -c "import sys; sys.path.insert(0, r'$currentDir'); from antigravity_bridge import AntigravityBridge; b = AntigravityBridge(); p, _ = b.discover(); print(f'PORT:{p}')" 2>&1
if ($bridgeOutput -match "PORT:(\d+)") {
    $detectedPort = $matches[1]
    Write-Host "  * Antigravity Baglanti : " -NoNewline
    Write-Host "BAGLI (Port $detectedPort)" -ForegroundColor Green
    Write-Host "  * Calisma Modu         : Yuksek Basarimli Yerel Antigravity Dil Sunucusu"
} else {
    Write-Host "  * Antigravity Baglanti : " -NoNewline
    Write-Host "KAPALI / BEKLEMEDE" -ForegroundColor Yellow
    Write-Host "  * Calisma Modu         : Universal Speech Recognition (Hibrit Yedek Motor)"
}

Write-Host ""

# 4. LOG & SAGLIK KONTROLU
Write-Host "[4] LOG VE SAGLIK:" -ForegroundColor Yellow
$logPath = Join-Path $currentDir "app.log"
if (Test-Path $logPath) {
    $logSize = [math]::Round(((Get-Item $logPath).Length / 1KB), 2)
    Write-Host "  * app.log Boyutu       : $logSize KB"
    Write-Host "  * Son 3 Log Kaydi      :"
    $lastLines = Get-Content $logPath -Tail 3 -ErrorAction SilentlyContinue
    foreach ($line in $lastLines) {
        Write-Host "     $line" -ForegroundColor DarkGray
    }
} else {
    Write-Host "  * app.log              : Henuz olusmadi."
}

Write-Host "========================================================================" -ForegroundColor Cyan
