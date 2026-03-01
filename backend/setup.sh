#!/bin/bash

# Change to the directory where the script is located
cd "$(dirname "$0")" || exit 1

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment"
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

echo "Activating virtual environment"
source venv/bin/activate

# Verify activation
if [ -z "$VIRTUAL_ENV" ]; then
    echo "ERROR: venv activation failed"
    exit 1
fi

echo "Upgrading pip"
python -m pip install --upgrade pip

echo "Installing dependencies"
pip install -r requirements.txt

echo "Setup Complete. To start the server, run: ./start.sh"