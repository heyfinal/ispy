#!/bin/bash

# Quick Build Script for iSpy SwiftUI App
# Simple version that opens Xcode for manual building

echo "🚀 iSpy Quick Build"
echo "==================="

PROJECT_DIR="/Users/daniel/claude/ispy/iSpyGUI"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Error: GUI directory not found"
    exit 1
fi

cd "$PROJECT_DIR"

echo "📱 Opening Xcode to build iSpy..."
echo ""
echo "🔧 Manual Steps:"
echo "1. Xcode will open"
echo "2. File → New → Project"
echo "3. macOS → App → Next"
echo "4. Product Name: iSpy"
echo "5. Interface: SwiftUI"
echo "6. Language: Swift"
echo "7. Replace ContentView.swift with our files"
echo "8. Add all .swift files from this directory"
echo "9. Press ⌘+R to build and run!"
echo ""

# Open Xcode
if command -v open &> /dev/null; then
    open -a Xcode .
    echo "✅ Xcode opened! Follow the steps above."
else
    echo "❌ Could not open Xcode automatically"
    echo "Please open Xcode manually and create a new project"
fi

echo ""
echo "💡 All SwiftUI source files are ready in: $PROJECT_DIR"
echo "🎨 Your app will have dark mode, AI chat, analytics, and more!"