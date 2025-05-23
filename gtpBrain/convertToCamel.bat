@echo off
:: Navigate to the directory where your Python script lives
cd /d C:\Users\jeffv\second_brain\gtp_brain

:: Run the Python script with any arguments you pass to the .bat
python camel_case_converter.py %*

:: Keep the terminal open so you can read the output
pause