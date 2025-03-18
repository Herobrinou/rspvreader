@echo off
echo Installing Speed Reader Pro...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed! Please install Python 3.8 or higher.
    echo You can download Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Create data directories if they don't exist
echo Creating data directories...
mkdir "data\books" 2>nul
mkdir "data\stats" 2>nul

REM Install required packages
echo Installing required packages...
pip install -r requirements.txt

REM Create desktop shortcut
echo Creating desktop shortcut...
set SCRIPT_PATH=%~dp0
set DESKTOP_PATH=%USERPROFILE%\Desktop
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%DESKTOP_PATH%\Speed Reader Pro.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%SCRIPT_PATH%run_speedreader.bat" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%SCRIPT_PATH%" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript //nologo CreateShortcut.vbs
del CreateShortcut.vbs

echo.
echo Installation completed successfully!
echo A shortcut has been created on your desktop.
echo You can now run Speed Reader Pro by:
echo 1. Double-clicking the desktop shortcut
echo 2. Running run_speedreader.bat
echo 3. Or using the command: python src/speedreader.py
echo.
pause 