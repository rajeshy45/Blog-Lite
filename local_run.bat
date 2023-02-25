@echo off

echo "Starting the application..."

if exist .env\ (echo "Enabling virtual env") else (
    echo "No Virtual env. Please run setup.sh first"
    exit N
)

:: Activate virtual env
call .env\Scripts\activate.bat
python main.py
call .env\Scripts\deactivate.bat
