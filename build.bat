@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Building executable...
pyinstaller --onefile --windowed --name "桌面日历" --add-data "database.py;." main.py

echo.
echo Done! Executable is in the dist\ folder.
pause
