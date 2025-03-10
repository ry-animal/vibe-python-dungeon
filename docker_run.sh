#!/bin/bash
# Script to build and run Dungeon Descent in Docker

set -e  # Exit immediately if a command exits with a non-zero status

MODE=${1:-"2d"}  # Default to 2D mode if no argument provided

# Check if the mode is valid
if [[ "$MODE" != "2d" && "$MODE" != "3d" ]]; then
    echo "Invalid mode: $MODE"
    echo "Usage: $0 [2d|3d]"
    exit 1
fi

echo "Building Dungeon Descent Docker image..."
docker build -t dungeon-descent .

if [[ "$MODE" == "2d" ]]; then
    echo "Running Dungeon Descent in 2D mode..."
    docker run --rm -it dungeon-descent
else
    echo "Running Dungeon Descent in 3D mode..."
    
    # Check if we're on macOS
    if [[ "$(uname)" == "Darwin" ]]; then
        echo "Running on macOS. To run 3D mode, please install XQuartz and set it up for X11 forwarding."
        echo "Instructions: https://stackoverflow.com/questions/37826094/xt-error-cant-open-display-if-using-default-display"
        
        # On macOS with XQuartz set up properly, you might use:
        # ip=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')
        # xhost + $ip
        # docker run --rm -it -e DISPLAY=$ip:0 dungeon-descent 3d
        
        read -p "Do you want to try running anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        
        # Try using the host's IP as the display
        ip=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')
        echo "Using host IP: $ip"
        xhost + $ip 2>/dev/null || echo "Warning: xhost command failed. X11 forwarding may not work."
        docker run --rm -it -e DISPLAY=$ip:0 dungeon-descent 3d
    else
        # Linux/Unix with X11
        echo "Running with X11 forwarding..."
        xhost +local:docker 2>/dev/null || echo "Warning: xhost command failed. X11 forwarding may not work."
        docker run --rm -it -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix dungeon-descent 3d
    fi
fi 