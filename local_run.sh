#! /bin/sh
echo "Starting the application..."

if [ -d ".env" ]; then
    echo "Enabling virtual env"
else
    echo "No Virtual env. Please run setup.sh first"
    # shellcheck disable=SC2242
    exit N
fi

# Activate virtual env
. .env/bin/activate
export ENV=development
python main.py
deactivate
