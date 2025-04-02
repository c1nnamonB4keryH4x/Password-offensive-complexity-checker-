@echo off
SETLOCAL

REM Check if Python is installed
where python >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Installing Python...
    REM Download Python installer (replace with the latest version link)
    curl -o python-installer.exe https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe
    REM Install Python silently
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    IF %ERRORLEVEL% NEQ 0 (
        echo Failed to install Python. Please install it manually.
        exit /b 1
    )
)

REM Check if pip is installed
where pip >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo pip is not installed. Installing pip...
    curl -o get-pip.py https://bootstrap.pypa.io/get-pip.py
    python get-pip.py
    IF %ERRORLEVEL% NEQ 0 (
        echo Failed to install pip. Please install it manually.
        exit /b 1
    )
)

REM Check if tkinter is installed
python -c "import tkinter" >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo tkinter is not installed. Please install it using the following command:
    echo For Windows, tkinter is usually included with Python installations.
    echo If you encounter issues, please install Python from the official website.
    exit /b 1
)

REM Install required Python packages
echo Installing required Python packages...
pip install -r requirements.txt

echo All dependencies have been installed successfully.
ENDLOCAL
