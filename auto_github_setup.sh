#!/bin/bash

# iSpy GitHub Auto-Setup Script
# Automatically creates and populates GitHub repository

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
echo -e "${CYAN}"
echo "  ╔═══════════════════════════════════════════════════════════════╗"
echo "  ║                    🕵️  iSpy GitHub Setup 🕵️                    ║"
echo "  ║           Advanced iOS Diagnostic Tool Repository            ║"
echo "  ╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Get GitHub token
echo -e "${YELLOW}🔐 GitHub Personal Access Token Required${NC}"
echo -e "${BLUE}Please enter your GitHub Personal Access Token:${NC}"
echo -e "${PURPLE}(Token needs 'repo' scope permissions)${NC}"
read -s -p "Token: " GITHUB_TOKEN
echo ""

if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}❌ Error: GitHub token is required${NC}"
    exit 1
fi

# Get GitHub username
echo -e "${BLUE}Please enter your GitHub username:${NC}"
read -p "Username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo -e "${RED}❌ Error: GitHub username is required${NC}"
    exit 1
fi

# Repository details
REPO_NAME="ispy"
REPO_DESCRIPTION="🕵️ Advanced iOS Diagnostic & Management Tool with AI Integration - The most comprehensive iOS device analysis toolkit with SwiftUI GUI"

echo ""
echo -e "${GREEN}📋 Repository Configuration:${NC}"
echo -e "   Repository: ${CYAN}$GITHUB_USERNAME/$REPO_NAME${NC}"
echo -e "   Description: ${PURPLE}$REPO_DESCRIPTION${NC}"
echo ""

# Navigate to project directory
PROJECT_DIR="/Users/daniel/claude/ispy"
cd "$PROJECT_DIR"

echo -e "${YELLOW}🏗️  Setting up local Git repository...${NC}"

# Initialize git if needed
if [ ! -d ".git" ]; then
    git init
    echo -e "${GREEN}✅ Git repository initialized${NC}"
else
    echo -e "${GREEN}✅ Git repository already exists${NC}"
fi

# Configure git user if not set
if [ -z "$(git config user.name)" ]; then
    git config user.name "$GITHUB_USERNAME"
    echo -e "${GREEN}✅ Git username configured${NC}"
fi

if [ -z "$(git config user.email)" ]; then
    echo -e "${BLUE}Enter your email for Git commits:${NC}"
    read -p "Email: " GIT_EMAIL
    git config user.email "$GIT_EMAIL"
    echo -e "${GREEN}✅ Git email configured${NC}"
fi

# Add all files
echo -e "${YELLOW}📦 Adding files to Git...${NC}"
git add .

# Create commit if there are changes
if git diff --staged --quiet; then
    echo -e "${YELLOW}⚠️  No changes to commit${NC}"
else
    echo -e "${YELLOW}💾 Creating initial commit...${NC}"
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

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
    echo -e "${GREEN}✅ Initial commit created${NC}"
fi

# Create GitHub repository
echo -e "${YELLOW}🌐 Creating GitHub repository...${NC}"

REPO_JSON=$(cat <<EOF
{
  "name": "$REPO_NAME",
  "description": "$REPO_DESCRIPTION",
  "private": false,
  "has_issues": true,
  "has_projects": true,
  "has_wiki": true,
  "auto_init": false,
  "homepage": "https://github.com/$GITHUB_USERNAME/$REPO_NAME",
  "topics": [
    "ios",
    "diagnostics", 
    "swiftui",
    "python",
    "ai",
    "mobile-device-management",
    "macos",
    "device-analysis",
    "troubleshooting",
    "analytics"
  ]
}
EOF
)

# Create repository using GitHub API
HTTP_STATUS=$(curl -s -w "%{http_code}" -o /tmp/repo_response.json \
  -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  -d "$REPO_JSON" \
  "https://api.github.com/user/repos")

if [ "$HTTP_STATUS" -eq 201 ]; then
    echo -e "${GREEN}✅ GitHub repository created successfully${NC}"
elif [ "$HTTP_STATUS" -eq 422 ]; then
    echo -e "${YELLOW}⚠️  Repository already exists, continuing...${NC}"
else
    echo -e "${RED}❌ Error creating repository (HTTP $HTTP_STATUS)${NC}"
    cat /tmp/repo_response.json
    exit 1
fi

# Add remote origin
echo -e "${YELLOW}🔗 Adding remote origin...${NC}"
if git remote get-url origin &>/dev/null; then
    git remote set-url origin "https://$GITHUB_TOKEN@github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    echo -e "${GREEN}✅ Remote origin updated${NC}"
else
    git remote add origin "https://$GITHUB_TOKEN@github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    echo -e "${GREEN}✅ Remote origin added${NC}"
fi

# Set main branch
echo -e "${YELLOW}🌿 Setting main branch...${NC}"
git branch -M main
echo -e "${GREEN}✅ Main branch set${NC}"

# Push to GitHub
echo -e "${YELLOW}🚀 Pushing to GitHub...${NC}"
if git push -u origin main; then
    echo -e "${GREEN}✅ Successfully pushed to GitHub${NC}"
else
    echo -e "${RED}❌ Error pushing to GitHub${NC}"
    exit 1
fi

# Create release (optional)
echo -e "${BLUE}Would you like to create an initial release? (y/n):${NC}"
read -p "Create release: " CREATE_RELEASE

if [[ "$CREATE_RELEASE" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🏷️  Creating initial release...${NC}"
    
    RELEASE_JSON=$(cat <<EOF
{
  "tag_name": "v1.0.0",
  "target_commitish": "main",
  "name": "🎉 iSpy v1.0.0 - Initial Release",
  "body": "## 🕵️ iSpy - Advanced iOS Diagnostic Tool\n\n### ✨ Features\n- 🐍 **Comprehensive Python Backend** - 10+ diagnostic modules\n- 🎨 **Elegant SwiftUI GUI** - Dark mode with beautiful animations\n- 🧠 **AI-Powered Diagnostics** - GPT integration for smart troubleshooting\n- 📊 **Advanced Analytics** - Trend visualization and predictive insights\n- 📱 **Real-time Monitoring** - Live device health tracking\n- 🛡️ **Security Analysis** - Complete device security assessment\n- 🔧 **Modular Architecture** - Extensible plugin system\n\n### 🚀 Quick Start\n1. Clone the repository\n2. Run the installation script: \`./install.sh\`\n3. Connect your iOS device via USB\n4. Launch iSpy: \`ispy --interactive\`\n\n### 📋 Requirements\n- macOS 10.15+\n- Python 3.8+\n- iOS device with USB connection\n- Xcode 15+ (for GUI)\n\n**The most comprehensive iOS diagnostic tool available!** 🎯",
  "draft": false,
  "prerelease": false
}
EOF
)

    HTTP_STATUS=$(curl -s -w "%{http_code}" -o /tmp/release_response.json \
      -X POST \
      -H "Authorization: token $GITHUB_TOKEN" \
      -H "Accept: application/vnd.github.v3+json" \
      -d "$RELEASE_JSON" \
      "https://api.github.com/repos/$GITHUB_USERNAME/$REPO_NAME/releases")

    if [ "$HTTP_STATUS" -eq 201 ]; then
        echo -e "${GREEN}✅ Initial release created${NC}"
    else
        echo -e "${YELLOW}⚠️  Could not create release (HTTP $HTTP_STATUS)${NC}"
    fi
fi

# Success message
echo ""
echo -e "${GREEN}"
echo "  ╔═══════════════════════════════════════════════════════════════╗"
echo "  ║                    🎉 SUCCESS! 🎉                            ║"
echo "  ║              iSpy Repository Created Successfully             ║"
echo "  ╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${CYAN}🔗 Repository URL: ${GREEN}https://github.com/$GITHUB_USERNAME/$REPO_NAME${NC}"
echo -e "${CYAN}📱 Clone Command: ${YELLOW}git clone https://github.com/$GITHUB_USERNAME/$REPO_NAME.git${NC}"
echo ""

echo -e "${BLUE}📋 What's been set up:${NC}"
echo -e "   ✅ GitHub repository created"
echo -e "   ✅ All files committed and pushed"
echo -e "   ✅ Topics and description added"
echo -e "   ✅ Issues, Projects, and Wiki enabled"
if [[ "$CREATE_RELEASE" =~ ^[Yy]$ ]]; then
    echo -e "   ✅ Initial release v1.0.0 created"
fi
echo ""

echo -e "${PURPLE}🚀 Next Steps:${NC}"
echo -e "   1. Visit your repository: ${GREEN}https://github.com/$GITHUB_USERNAME/$REPO_NAME${NC}"
echo -e "   2. Add repository secrets for CI/CD (if needed)"
echo -e "   3. Configure branch protection rules"
echo -e "   4. Set up GitHub Pages (optional)"
echo -e "   5. Build the SwiftUI app in Xcode"
echo ""

echo -e "${YELLOW}📱 To build the .app:${NC}"
echo -e "   cd $PROJECT_DIR/iSpyGUI"
echo -e "   open iSpy.xcodeproj"
echo -e "   # In Xcode: Product → Archive → Distribute App"
echo ""

echo -e "${GREEN}🎯 Your advanced iOS diagnostic tool is now live on GitHub! 🕵️${NC}"

# Clean up
rm -f /tmp/repo_response.json /tmp/release_response.json

# Open repository in browser (optional)
echo -e "${BLUE}Would you like to open the repository in your browser? (y/n):${NC}"
read -p "Open browser: " OPEN_BROWSER

if [[ "$OPEN_BROWSER" =~ ^[Yy]$ ]]; then
    open "https://github.com/$GITHUB_USERNAME/$REPO_NAME"
fi

echo -e "${CYAN}Thank you for using iSpy GitHub Auto-Setup! 🚀${NC}"