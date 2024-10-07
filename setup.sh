#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting setup..."

# Step 1: Create a virtual environment in venv/tradepy (if it doesn't exist)
if [ ! -d "venv/tradepy" ]; then
    echo "Creating virtual environment in venv/tradepy..."
    python3 -m venv venv/tradepy || { echo "Failed to create virtual environment"; exit 1; }
    echo "Virtual environment created."
else
    echo "Virtual environment already exists in venv/tradepy."
fi

# Step 2: Activate the virtual environment
echo "Activating virtual environment..."
source venv/tradepy/bin/activate || { echo "Failed to activate virtual environment"; exit 1; }

# Step 3: Upgrade pip and ensure required tools are installed
echo "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel -v || { echo "Failed to upgrade pip, setuptools, or wheel"; exit 1; }

# Step 4: Install dependencies from requirements.txt, if it exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt -v || { echo "Failed to install dependencies from requirements.txt"; exit 1; }
else
    echo "No requirements.txt found. Skipping dependency installation."
fi

# Step 5: Install the project as an editable package
if [ -f "pyproject.toml" ]; then
    echo "Installing the project with pyproject.toml..."
    pip install -e . --use-pep517 -v || { echo "Failed to install project with pyproject.toml"; exit 1; }
else
    echo "No pyproject.toml found. Falling back to setup.py..."
    pip install -e . -v || { echo "Failed to install project with setup.py"; exit 1; }
fi

echo "Setup complete. Virtual environment is ready."

## Step 6: Automatically activate the virtual environment for the user
#echo "Automatically activating the virtual environment..."
#exec bash --rcfile <(echo "source venv/tradepy/bin/activate")
