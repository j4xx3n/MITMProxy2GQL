#!/bin/bash

# --- Installation Script for Graphql MITMProxy Tools ---

# Set the name for the virtual environment directory
VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"

echo "### Starting setup for GraphQL MITMProxy Tools ###"
echo " "

# 1. Check for Python 3
if ! command -v python3 &> /dev/null
then
    echo "ERROR: python3 could not be found. Please install Python 3 and try again."
    exit 1
fi

# 2. Check for pip
if ! command -v pip3 &> /dev/null
then
    echo "WARNING: pip3 could not be found. Attempting to install required packages globally."
    # Attempt a global install as a fallback
    echo "Installing dependencies globally (requires sudo/root)..."
    sudo python3 -m pip install -r $REQUIREMENTS_FILE
else
    # 3. Create and activate a Python Virtual Environment
    echo "Creating virtual environment in '$VENV_DIR'..."
    python3 -m venv $VENV_DIR
    source $VENV_DIR/bin/activate
    
    # 4. Install dependencies from requirements.txt
    echo "Installing required Python packages..."
    pip install -r $REQUIREMENTS_FILE
    
    # 5. Check if installation was successful
    if [ $? -eq 0 ]; then
        echo " "
        echo "[+] Python dependencies installed successfully!"
    else
        echo " "
        echo "[!] ERROR: Failed to install Python dependencies. Check the error output above."
        deactivate # Exit the virtual environment on failure
        exit 1
    fi
fi

# 6. Make the main scripts executable
echo "Setting executable permissions for parser.py and proxy.py..."
chmod +x parser.py proxy.py

echo " "
echo "### Installation Complete! ###"
echo "To run the proxy, use: "
echo "source $VENV_DIR/bin/activate && ./proxy.py"
echo " "