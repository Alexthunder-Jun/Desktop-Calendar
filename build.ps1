# build.ps1 — Windows .exe build script
# Usage: powershell -ExecutionPolicy Bypass -File build.ps1

$ErrorActionPreference = "Stop"

Write-Host "===== 桌面日历 Build =====" -ForegroundColor Cyan

# 1. Install deps
Write-Host "`n[1/3] Installing dependencies..."
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "pip install failed" }

# 2. Run tests
Write-Host "`n[2/3] Running tests..."
python -m pytest tests/ -v
if ($LASTEXITCODE -ne 0) { throw "Tests failed" }

# 3. Build exe
Write-Host "`n[3/3] Building executable..."
pyinstaller daily_event.spec --noconfirm --clean
if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed" }

Write-Host "`n===== Build complete! =====" -ForegroundColor Green
Write-Host "Executable: dist\桌面日历.exe"
