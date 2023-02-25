@echo off

echo "Creating virtual environment and installing the required packages..."

if exist .env\ (echo ".env folder exists. Installing using pip") else (
    echo "creating .env and install using pip"
    py -m ensurepip --upgrade
    python -m venv .env
)

:: Activate virtual env
call .env\Scripts\activate.bat

:: Upgrade the PIP
python.exe -m pip install --upgrade pip
pip3 install -r requirements.txt

:: Work done. so deactivate the virtual env
call .env\Scripts\deactivate.bat
