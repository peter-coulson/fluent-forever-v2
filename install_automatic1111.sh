#!/bin/bash

# Automatic1111 Installation Script for macOS
# This installs Stable Diffusion WebUI with API support

echo "🎨 Automatic1111 Stable Diffusion WebUI Installer"
echo "=================================================="
echo ""
echo "⚠️  This will download several GB of data (models)"
echo "⚠️  Ensure you have at least 10GB free disk space"
echo ""
read -p "Continue with installation? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled"
    exit 1
fi

# Check prerequisites
echo "📍 Checking prerequisites..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "✅ Homebrew found"
fi

# Check Python version
if ! python3 --version | grep -E "3\.(8|9|10|11)" &> /dev/null; then
    echo "⚠️  Python 3.8-3.11 required. Current version:"
    python3 --version
    echo "Installing Python 3.10 via Homebrew..."
    brew install python@3.10
fi

# Install git if not present
if ! command -v git &> /dev/null; then
    echo "Installing git..."
    brew install git
fi

# Create installation directory
INSTALL_DIR="$HOME/stable-diffusion-webui"
echo ""
echo "📁 Installing to: $INSTALL_DIR"

# Clone repository
if [ -d "$INSTALL_DIR" ]; then
    echo "⚠️  Directory already exists. Updating..."
    cd "$INSTALL_DIR"
    git pull
else
    echo "📥 Cloning Automatic1111 repository..."
    git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Create launch script with API enabled
echo "📝 Creating launch script with API enabled..."
cat > launch_api.sh << 'EOF'
#!/bin/bash
# Launch Automatic1111 with API enabled for Fluent Forever

cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Launch with API enabled and specific settings
python3 launch.py \
    --api \
    --listen \
    --port 7860 \
    --enable-insecure-extension-access \
    --theme dark \
    --xformers \
    --no-half-vae
EOF

chmod +x launch_api.sh

# Download a base model (SD 1.5)
MODEL_DIR="$INSTALL_DIR/models/Stable-diffusion"
mkdir -p "$MODEL_DIR"

if [ ! -f "$MODEL_DIR/v1-5-pruned-emaonly.safetensors" ]; then
    echo ""
    echo "📥 Downloading Stable Diffusion 1.5 model (4GB)..."
    echo "This will take a while..."
    curl -L "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors" \
         -o "$MODEL_DIR/v1-5-pruned-emaonly.safetensors" \
         --progress-bar
else
    echo "✅ Base model already downloaded"
fi

# Create Quentin Blake style prompt template
STYLES_DIR="$INSTALL_DIR/styles"
mkdir -p "$STYLES_DIR"

cat > "$STYLES_DIR/quentin_blake.json" << 'EOF'
{
  "Quentin Blake Illustration": {
    "prompt": "illustration in the style of Quentin Blake, watercolor, whimsical, loose brushstrokes, energetic lines, {prompt}",
    "negative_prompt": "realistic, photographic, 3d render, dark, gloomy, horror"
  }
}
EOF

echo "✅ Created Quentin Blake style template"

# Create webui-user.sh for settings
cat > "$INSTALL_DIR/webui-user.sh" << 'EOF'
#!/bin/bash
# Settings for Automatic1111

# Command line arguments for launch.py
export COMMANDLINE_ARGS="--api --listen --port 7860 --enable-insecure-extension-access"

# Python path (adjust if using specific version)
#export python_cmd="python3.10"

# Optimize for Mac
export PYTORCH_ENABLE_MPS_FALLBACK=1
EOF

chmod +x "$INSTALL_DIR/webui-user.sh"

echo ""
echo "=================================================="
echo "✅ Installation complete!"
echo ""
echo "📍 Installation directory: $INSTALL_DIR"
echo ""
echo "🚀 To start Automatic1111 with API:"
echo "   cd $INSTALL_DIR"
echo "   ./launch_api.sh"
echo ""
echo "Or use the standard launcher:"
echo "   ./webui.sh"
echo ""
echo "🌐 Once running, access at:"
echo "   Web UI: http://localhost:7860"
echo "   API: http://localhost:7860/docs"
echo ""
echo "📝 Notes:"
echo "   - First launch will install dependencies (10-15 min)"
echo "   - API is enabled for Fluent Forever integration"
echo "   - Quentin Blake style template added"
echo ""
echo "🎨 Next steps for character LoRAs:"
echo "   1. Train LoRA models for your friends"
echo "   2. Place in: $INSTALL_DIR/models/Lora/"
echo "   3. Use in prompts: <lora:friend_name:0.8>"
echo ""
