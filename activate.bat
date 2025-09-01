@echo off
REM EvolvingTrader Virtual Environment Activation Script for Windows

echo 🚀 Activating EvolvingTrader Virtual Environment...

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run 'python setup.py' first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

echo ✅ Virtual environment activated!
echo.
echo You can now run:
echo   python main.py backtest    # Run backtest
echo   python main.py live        # Run live trading
echo   python main.py dashboard   # Run dashboard
echo.
echo To deactivate, run: deactivate
echo.

REM Keep the command prompt active
cmd /k