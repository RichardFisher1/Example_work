@echo off

:: Exit immediately if a command fails
setlocal enabledelayedexpansion
echo Starting setup...

:: Step 1: Create a virtual environment in venv\tradepy (if it doesn't exist)
if not exist "venv\tradepy" (
    echo Creating virtual environment in venv\tradepy...
    python -m venv venv\tradepy
    if %ERRORLEVEL% neq 0 (
        echo Failed to create virtual environment
        exit /b 1
    )
    echo Virtual environment created.
) else (
    echo Virtual environment already exists in venv\tradepy.
)

:: Step 2: Activate the virtual environment
echo Activating virtual environment...
call venv\tradepy\Scripts\activate
if %ERRORLEVEL% neq 0 (
    echo Failed to activate virtual environment
    exit /b 1
)

:: Step 3: Upgrade pip, setuptools, and wheel
echo Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel
if %ERRORLEVEL% neq 0 (
    echo Failed to upgrade pip, setuptools, or wheel
    exit /b 1
)

:: Step 4: Install dependencies from requirements.txt, if it exists
if exist "requirements.txt" (
    echo Installing dependencies from requirements.txt...
    python -m pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo Failed to install dependencies from requirements.txt
        exit /b 1
    )
) else (
    echo No requirements.txt found. Skipping dependency installation.
)

:: Step 5: Install the project as an editable package
if exist "pyproject.toml" (
    echo Installing the project with pyproject.toml...
    python -m pip install -e . --use-pep517
    if %ERRORLEVEL% neq 0 (
        echo Failed to install project with pyproject.toml
        exit /b 1
    )
) else if exist "setup.py" (
    echo Installing the project with setup.py...
    python -m pip install -e .
    if %ERRORLEVEL% neq 0 (
        echo Failed to install project with setup.py
        exit /b 1
    )
) else (
    echo No pyproject.toml or setup.py found. Skipping project installation.
)

echo Setup complete. Virtual environment is ready.

:: Step 6: Automatically activate the virtual environment for the user
echo Activating the virtual environment for you...
call venv\tradepy\Scripts\activate