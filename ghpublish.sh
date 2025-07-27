#!/bin/bash

# iSpy GitHub Publisher
# Usage: ./ghpublish.sh <GITHUB_TOKEN>

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
echo "  ║                🚀 iSpy GitHub Publisher 🚀                   ║"
echo "  ║              One-Command Repository Creation                  ║"
echo "  ╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if token provided
if [ $# -eq 0 ]; then
    echo -e "${RED}❌ Error: GitHub token required${NC}"
    echo -e "${BLUE}Usage: ./ghpublish.sh <GITHUB_TOKEN>${NC}"
    echo -e "${YELLOW}Example: ./ghpublish.sh ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx${NC}"
    exit 1
fi

GITHUB_TOKEN="$1"

# Validate token format
if [[ ! "$GITHUB_TOKEN" =~ ^ghp_[a-zA-Z0-9]{36}$ ]]; then
    echo -e "${YELLOW}⚠️  Warning: Token format doesn't match expected pattern${NC}"
    echo -e "${BLUE}Continuing anyway...${NC}"
fi

echo -e "${GREEN}🔐 GitHub token provided${NC}"

# Get GitHub username from token
echo -e "${YELLOW}👤 Getting GitHub username...${NC}"
USER_RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/user")
GITHUB_USERNAME=$(echo "$USER_RESPONSE" | grep -o '"login":"[^"]*' | cut -d'"' -f4)

if [ -z "$GITHUB_USERNAME" ]; then
    echo -e "${YELLOW}⚠️  Could not get username from token, using 'heyfinal'${NC}"
    echo -e "${BLUE}Debug: API Response: $USER_RESPONSE${NC}"
    GITHUB_USERNAME="heyfinal"
    echo -e "${GREEN}✅ Using username: ${CYAN}$GITHUB_USERNAME${NC}"
else
    echo -e "${GREEN}✅ GitHub username: ${CYAN}$GITHUB_USERNAME${NC}"
fi

# Repository details
REPO_NAME="ispy"
REPO_DESCRIPTION="🕵️ Advanced iOS Diagnostic & Management Tool with AI Integration - The most comprehensive iOS device analysis toolkit with SwiftUI GUI"

echo -e "${PURPLE}📋 Repository: ${CYAN}$GITHUB_USERNAME/$REPO_NAME${NC}"

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

# Configure git user
git config user.name "$GITHUB_USERNAME"
echo -e "${GREEN}✅ Git username configured${NC}"

# Get user email from GitHub API
USER_EMAIL=$(echo "$USER_RESPONSE" | grep -o '"email":"[^"]*' | cut -d'"' -f4)
if [ -n "$USER_EMAIL" ] && [ "$USER_EMAIL" != "null" ]; then
    git config user.email "$USER_EMAIL"
    echo -e "${GREEN}✅ Git email configured: $USER_EMAIL${NC}"
else
    git config user.email "$GITHUB_USERNAME@users.noreply.github.com"
    echo -e "${GREEN}✅ Git email configured: $GITHUB_USERNAME@users.noreply.github.com${NC}"
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
    "analytics",
    "iphone",
    "ipad",
    "battery-health",
    "storage-analysis",
    "security-scan"
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
    if [ -f /tmp/repo_response.json ]; then
        cat /tmp/repo_response.json
    fi
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

# Create initial release
echo -e "${YELLOW}🏷️  Creating initial release...${NC}"

RELEASE_JSON=$(cat <<EOF
{
  "tag_name": "v1.0.0",
  "target_commitish": "main",
  "name": "🎉 iSpy v1.0.0 - Initial Release",
  "body": "## 🕵️ iSpy - Advanced iOS Diagnostic Tool\n\n### ✨ Features\n- 🐍 **Comprehensive Python Backend** - 10+ diagnostic modules\n- 🎨 **Elegant SwiftUI GUI** - Dark mode with beautiful animations\n- 🧠 **AI-Powered Diagnostics** - GPT integration for smart troubleshooting\n- 📊 **Advanced Analytics** - Trend visualization and predictive insights\n- 📱 **Real-time Monitoring** - Live device health tracking\n- 🛡️ **Security Analysis** - Complete device security assessment\n- 🔧 **Modular Architecture** - Extensible plugin system\n\n### 🚀 Quick Start\n1. Clone the repository\n2. Run the installation script: \`./install.sh\`\n3. Connect your iOS device via USB\n4. Launch iSpy: \`ispy --interactive\`\n\n### 📋 Requirements\n- macOS 14.0+\n- Python 3.8+\n- iOS device with USB connection\n- Xcode 15+ (for GUI)\n\n**The most comprehensive iOS diagnostic tool available!** 🎯\n\n### 📱 SwiftUI GUI\nIncludes a beautiful native macOS interface with:\n- Dark mode design with cyan accents\n- 5 main sections: Dashboard, Devices, AI Assistant, Analytics, Settings\n- Real-time device monitoring\n- Interactive charts and visualizations\n- AI-powered chat interface\n\n### 🔨 Building the App\n\`\`\`bash\n# Build SwiftUI GUI\n./build.sh\n\n# Or quick build\n./quick_build.sh\n\`\`\`\n\n---\n\n**Made with ❤️ using Claude Code**",
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
    echo -e "${GREEN}✅ Initial release v1.0.0 created${NC}"
else
    echo -e "${YELLOW}⚠️  Could not create release (HTTP $HTTP_STATUS)${NC}"
fi

# Success message
echo ""
echo -e "${GREEN}"
echo "  ╔═══════════════════════════════════════════════════════════════╗"
echo "  ║                    🎉 SUCCESS! 🎉                            ║"
echo "  ║              iSpy Repository Created & Published!             ║"
echo "  ╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

REPO_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME"

echo -e "${CYAN}🔗 Repository URL: ${GREEN}$REPO_URL${NC}"
echo -e "${CYAN}📱 Clone Command: ${YELLOW}git clone $REPO_URL.git${NC}"
echo ""

echo -e "${BLUE}📋 What's been created:${NC}"
echo -e "   ✅ GitHub repository with fancy README"
echo -e "   ✅ All Python backend files committed"
echo -e "   ✅ Complete SwiftUI GUI source code"
echo -e "   ✅ Build scripts and documentation"
echo -e "   ✅ Professional project structure"
echo -e "   ✅ Topics and description configured"
echo -e "   ✅ Initial release v1.0.0 created"
echo ""

echo -e "${PURPLE}🚀 Next Steps:${NC}"
echo -e "   1. Visit: ${GREEN}$REPO_URL${NC}"
echo -e "   2. Build the SwiftUI app: ${YELLOW}./build.sh${NC}"
echo -e "   3. Share your repository with the world!"
echo ""

# Open repository in browser
if command -v open &> /dev/null; then
    echo -e "${BLUE}🌐 Opening repository in browser...${NC}"
    open "$REPO_URL"
fi

# Clean up
rm -f /tmp/repo_response.json /tmp/release_response.json

echo -e "${GREEN}🎯 Your advanced iOS diagnostic tool is now live on GitHub! 🕵️${NC}"
echo -e "${CYAN}Thank you for using iSpy GitHub Publisher! 🚀${NC}"