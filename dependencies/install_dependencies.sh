#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python3 is installed
if ! command_exists python3; then
    echo "Python3 is not installed. Installing Python3..."
    # For Ubuntu/Debian
    sudo apt-get update
    sudo apt-get install python3 python3-pip python3-tk -y
else
    echo "Python3 is already installed."
fi

# Check if pip is installed
if ! command_exists pip3; then
    echo "pip is not installed. Installing pip..."
    sudo apt-get install python3-pip -y
else
    echo "pip is already installed."
fi

# Check if tkinter is installed
if ! python3 -c "import tkinter" &> /dev/null; then
    echo "tkinter is not installed. Installing tkinter..."
    sudo apt-get install python3-tk -y
else
    echo "tkinter is already installed."
fi

# Install required Python packages
echo "Installing required Python packages..."
pip3 install -r requirements.txt

echo "All dependencies have been installed successfully."
