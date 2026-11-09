@echo off
cd /d "%~dp0"

echo ==== Step 1: Checking for Python 3.12 ====
py -3.12 --version >nul 2>&1
if errorlevel 1 (
    echo Python 3.12 not found. Installing it with winget...
    winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo.
        echo Automatic install failed. Please install Python 3.12 64-bit from python.org,
        echo then double-click setup.bat again.
        pause
        exit /b 1
    )
    echo.
    echo Python 3.12 installed. Close this window and double-click setup.bat again.
    pause
    exit /b 0
)
py -3.12 --version

echo.
echo ==== Step 2: Creating virtual environment (venv) ====
if not exist venv (
    py -3.12 -m venv venv
)
call venv\Scripts\activate.bat
python --version

echo.
echo ==== Step 3: Installing libraries (this can take a few minutes) ====
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Library installation failed. Copy the error above and send it.
    pause
    exit /b 1
)

echo.
echo ==== Step 4: Building the vector index ====
if not exist .env (
    echo .env file not found. Create it with your OPENAI_API_KEY,
    echo then double-click setup.bat again.
    pause
    exit /b 1
)
python ingest.py
if errorlevel 1 (
    echo.
    echo Index build failed. Copy the error above and send it.
    pause
    exit /b 1
)

echo.
echo ==== Done! Double-click run.bat to start the bot ====
pause
