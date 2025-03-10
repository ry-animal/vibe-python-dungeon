#!/bin/bash
# Script to install and run Dungeon Descent

set -e  # Exit immediately if a command exits with a non-zero status

MODE=${1:-"2d"}  # Default to 2D mode if no argument provided

# Check if the mode is valid
if [[ "$MODE" != "2d" && "$MODE" != "3d" ]]; then
    echo "Invalid mode: $MODE"
    echo "Usage: $0 [2d|3d]"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -e .

# Run the game
echo "Running Dungeon Descent in $MODE mode..."
if [ "$MODE" = "2d" ]; then
    python -m dungeon_descent.scripts.run_2d
else
    python -m dungeon_descent.scripts.run_3d
fi 