#!/bin/bash

# GitHub Repository Setup Script for iSpy
echo "🚀 Setting up iSpy GitHub repository..."

# Navigate to project directory
cd /Users/daniel/claude/ispy

# Initialize git repository if not already done
if [ ! -d ".git" ]; then
    echo "📝 Initializing Git repository..."
    git init
fi

# Add all files
echo "📦 Adding files to Git..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "🎉 Initial commit: iSpy - Advanced iOS Diagnostic Tool

✨ Features:
- 🐍 Comprehensive Python backend with 10+ diagnostic modules
- 🎨 Elegant SwiftUI GUI with dark mode design
- 🧠 AI-powered troubleshooting with GPT integration
- 📊 Advanced analytics with trend visualization
- 🔧 Modular architecture for extensibility
- 📱 Real-time device monitoring and diagnostics
- 🛡️ Security analysis and privacy-first design
- 📈 Predictive insights and recommendations

🚀 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

# Set up remote repository (you'll need to create this on GitHub first)
echo "🌐 Setting up remote repository..."
echo "Please create a new repository on GitHub named 'ispy' then run:"
echo "git remote add origin https://github.com/YOUR_USERNAME/ispy.git"
echo "git branch -M main"
echo "git push -u origin main"

echo ""
echo "🔧 Manual Steps Required:"
echo "1. Go to https://github.com/new"
echo "2. Repository name: ispy"
echo "3. Description: Advanced iOS Diagnostic & Management Tool with AI Integration"
echo "4. Set to Public"
echo "5. Don't initialize with README (we already have one)"
echo "6. Click 'Create repository'"
echo "7. Run the git remote commands shown above"
echo ""
echo "📱 To build the .app:"
echo "1. cd iSpyGUI"
echo "2. open iSpy.xcodeproj"
echo "3. In Xcode: Product > Archive > Distribute App"
echo ""
echo "✅ Setup complete! Your iSpy project is ready for GitHub! 🎉"