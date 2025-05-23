@echo off
setlocal enabledelayedexpansion
title Second Brain camelCase Converter

echo =======================================
echo  Second Brain camelCase Converter
echo =======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3 and try again
    pause
    exit /b 1
)

REM Set the script path - assumed to be in the same directory as this batch file
set "SCRIPT_DIR=%~dp0"
set "PYTHON_SCRIPT=%SCRIPT_DIR%second_brain_converter.py"

REM Check if the Python script exists
if not exist "%PYTHON_SCRIPT%" (
    echo ERROR: second_brain_converter.py not found in the same directory
    echo Please make sure both files are in the same folder
    pause
    exit /b 1
)

:menu
echo.
echo Select an option:
echo 1. Run Dry Run (show what would change without making changes)
echo 2. Run Full Conversion (with backup)
echo 3. Run Full Conversion (no backup - NOT RECOMMENDED)
echo 4. Exit
echo.

set /p CHOICE="Enter choice (1-4): "

if "%CHOICE%"=="1" (
    echo.
    echo Running in DRY RUN mode - No changes will be made
    echo This will show you what would be renamed
    echo.
    pause
    python "%PYTHON_SCRIPT%" --dry-run
    goto end
) else if "%CHOICE%"=="2" (
    echo.
    echo Running FULL CONVERSION with backup
    echo This will create a backup and then convert all files
    echo.
    echo WARNING: This will rename files and folders in your second_brain directory
    set /p CONFIRM="Are you sure you want to continue? (y/n): "
    if /i "!CONFIRM!"=="y" (
        python "%PYTHON_SCRIPT%"
    ) else (
        echo Operation cancelled.
    )
    goto end
) else if "%CHOICE%"=="3" (
    echo.
    echo WARNING: Running without backup is NOT RECOMMENDED
    echo This could lead to data loss if something goes wrong
    echo.
    set /p CONFIRM="Are you REALLY sure you want to continue without backup? (y/n): "
    if /i "!CONFIRM!"=="y" (
        set /p DOUBLE_CONFIRM="Type 'CONFIRM' in all caps to proceed: "
        if "!DOUBLE_CONFIRM!"=="CONFIRM" (
            python "%PYTHON_SCRIPT%" --no-backup
        ) else (
            echo Operation cancelled.
        )
    ) else (
        echo Operation cancelled.
    )
    goto end
) else if "%CHOICE%"=="4" (
    echo.
    echo Exiting...
    exit /b 0
) else (
    echo.
    echo Invalid choice. Please try again.
    goto menu
)

:end
echo.
echo Conversion process completed.
echo.
echo Press any key to return to menu...
pause >nul
goto menu