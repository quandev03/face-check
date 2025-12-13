#!/bin/bash
# Build script for both platforms (run on each platform)

echo "Face Recognition App - Build Script"
echo "===================================="
echo ""

# Detect platform
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS"
    ./build_mac.sh
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux"
    echo "Note: This script is primarily for Windows and macOS"
    echo "For Linux, you may need to adjust the build process"
    ./build_mac.sh  # Use similar process
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "Detected Windows"
    ./build_windows.bat
else
    echo "Unknown platform: $OSTYPE"
    echo "Please run the appropriate build script manually:"
    echo "  - Windows: build_windows.bat"
    echo "  - macOS: build_mac.sh"
    exit 1
fi





