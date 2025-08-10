#!/bin/bash

# Fluent Forever V2 - Setup Script
# This script installs required Python packages and checks system requirements

echo "🚀 Fluent Forever V2 - System Setup"
echo "===================================="
echo ""

# Check Python version
echo "📍 Checking Python version..."
python3 --version

# Install required packages
echo ""
echo "📦 Installing required Python packages..."
pip3 install requests pillow

# Check if Automatic1111 is installed
echo ""
echo "🎨 Checking for Automatic1111 WebUI..."
if lsof -i :7860 > /dev/null 2>&1; then
    echo "✅ Automatic1111 appears to be running on port 7860"
else
    echo "⚠️  Automatic1111 not detected on port 7860"
    echo "   Please ensure Automatic1111 WebUI is running"
    echo "   Repository: https://github.com/AUTOMATIC1111/stable-diffusion-webui"
fi

# Check if AnkiConnect is available
echo ""
echo "📚 Checking for AnkiConnect..."
if lsof -i :8765 > /dev/null 2>&1; then
    echo "✅ AnkiConnect appears to be running on port 8765"
else
    echo "⚠️  AnkiConnect not detected on port 8765"
    echo "   Please ensure Anki is running with AnkiConnect addon"
    echo "   Addon code: 2055492159"
fi

# Create media directories
echo ""
echo "📁 Creating media directories..."
mkdir -p media/images
mkdir -p media/audio
echo "✅ Media directories created"

# Make automation script executable
chmod +x automation.py
echo "✅ Made automation.py executable"

echo ""
echo "===================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your Forvo API key to config.json"
echo "2. Ensure Automatic1111 WebUI is running"
echo "3. Ensure Anki is running with AnkiConnect"
echo "4. Run: python3 automation.py status"
echo ""
