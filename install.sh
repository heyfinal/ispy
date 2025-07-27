#!/bin/bash

# iSpy Installation Script
# Comprehensive iOS Diagnostic & Management Tool

set -e

echo "🔧 Installing iSpy - Advanced iOS Diagnostic Tool"
echo "=================================================="

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: iSpy requires macOS to function properly"
    exit 1
fi

# Check for Python 3.8+
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3.8+ is required but not installed"
    echo "Please install Python from https://python.org or use Homebrew:"
    echo "brew install python"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if [[ $(echo "$PYTHON_VERSION < 3.8" | bc -l) -eq 1 ]]; then
    echo "❌ Error: Python $PYTHON_VERSION detected. Python 3.8+ required"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Check for Homebrew
if ! command -v brew &> /dev/null; then
    echo "⚠️  Homebrew not detected. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

echo "📦 Installing system dependencies..."

# Install libimobiledevice and related tools
brew_packages=(
    "libimobiledevice"
    "ideviceinstaller" 
    "ios-deploy"
    "usbmuxd"
    "libplist"
    "openssl"
)

for package in "${brew_packages[@]}"; do
    if brew list "$package" &>/dev/null; then
        echo "✅ $package already installed"
    else
        echo "📦 Installing $package..."
        brew install "$package"
    fi
done

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install iSpy package
echo "🔧 Installing iSpy package..."
pip install -e .

# Create symlink for global access
echo "🔗 Creating global command symlink..."
sudo ln -sf "$(pwd)/venv/bin/ispy" /usr/local/bin/ispy

# Set up configuration directory
echo "⚙️  Setting up configuration..."
mkdir -p ~/.ispy
mkdir -p ~/.ispy/modules
mkdir -p ~/.ispy/reports
mkdir -p ~/.ispy/backups

# Create default configuration
cat > ~/.ispy/config.yaml << EOF
# iSpy Configuration File
general:
  log_level: INFO
  auto_update: true
  backup_location: ~/.ispy/backups
  
ai:
  provider: openai
  model: gpt-4
  api_key_env: OPENAI_API_KEY
  
modules:
  enabled:
    - battery
    - storage
    - network
    - crashes
    - apps
    - security
    - performance
    - thermal
    - backup
    - accessibility
  
reporting:
  format: markdown
  include_graphs: true
  auto_save: true

notifications:
  critical_issues: true
  recommendations: true
EOF

# Set up bash completion
echo "🎯 Setting up command completion..."
cat > ~/.ispy/ispy-completion.bash << 'EOF'
# iSpy bash completion
_ispy_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    opts="--device --module --report --interactive --help --version"
    modules="battery storage network crashes apps security performance thermal backup accessibility"
    
    case "${prev}" in
        --module|-m)
            COMPREPLY=( $(compgen -W "${modules}" -- ${cur}) )
            return 0
            ;;
        --device|-d)
            # Get connected device UDIDs
            local devices=$(idevice_id -l 2>/dev/null || echo "")
            COMPREPLY=( $(compgen -W "${devices}" -- ${cur}) )
            return 0
            ;;
        *)
            ;;
    esac
    
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}
complete -F _ispy_completion ispy
EOF

# Add completion to bash profile
if [[ -f ~/.bash_profile ]]; then
    if ! grep -q "ispy-completion.bash" ~/.bash_profile; then
        echo "source ~/.ispy/ispy-completion.bash" >> ~/.bash_profile
    fi
fi

if [[ -f ~/.bashrc ]]; then
    if ! grep -q "ispy-completion.bash" ~/.bashrc; then
        echo "source ~/.ispy/ispy-completion.bash" >> ~/.bashrc
    fi
fi

# Create desktop shortcut
echo "🖥️  Creating desktop application..."
cat > ~/Desktop/iSpy.command << EOF
#!/bin/bash
cd "$(dirname "$0")"
source "$(pwd)/venv/bin/activate"
python3 ispy.py --interactive
EOF

chmod +x ~/Desktop/iSpy.command

# Create uninstall script
echo "🗑️  Creating uninstall script..."
cat > uninstall.sh << 'EOF'
#!/bin/bash
echo "Uninstalling iSpy..."
sudo rm -f /usr/local/bin/ispy
rm -rf ~/.ispy
rm -f ~/Desktop/iSpy.command
echo "iSpy uninstalled successfully"
EOF

chmod +x uninstall.sh

echo ""
echo "🎉 iSpy installation completed successfully!"
echo ""
echo "📋 Installation Summary:"
echo "========================"
echo "✅ System dependencies installed via Homebrew"
echo "✅ Python virtual environment created"
echo "✅ iSpy package installed"
echo "✅ Global command 'ispy' available"
echo "✅ Configuration created at ~/.ispy/"
echo "✅ Desktop shortcut created"
echo "✅ Bash completion enabled"
echo ""
echo "🚀 Getting Started:"
echo "=================="
echo "1. Connect your iOS device via USB"
echo "2. Trust this computer on your device"
echo "3. Run: ispy --interactive"
echo "   Or: ispy --help for all options"
echo ""
echo "⚙️  Configuration:"
echo "=================="
echo "• Config file: ~/.ispy/config.yaml"
echo "• Logs: ~/.ispy/ispy.log"
echo "• Reports: ~/.ispy/reports/"
echo ""
echo "🤖 AI Features:"
echo "==============="
echo "Set your OpenAI API key:"
echo "export OPENAI_API_KEY='your-api-key-here'"
echo "Add this to your ~/.bash_profile or ~/.bashrc"
echo ""
echo "📚 Documentation:"
echo "================="
echo "• Run 'ispy --help' for command options"
echo "• Check ~/.ispy/ for configuration examples"
echo "• Visit the GitHub repository for updates"
echo ""
echo "Happy iOS diagnostics! 🎯"