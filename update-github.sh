#!/bin/bash

# Update GitHub Repository with Latest Changes
# This script updates your existing repository with privacy improvements and dashboard updates

set -e

echo "================================================"
echo "Zyxel 5G Router Exporter - GitHub Update"
echo "================================================"
echo ""

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    echo "Please run this script from your project directory"
    exit 1
fi

echo "📋 Current git status:"
git status --short
echo ""

# Check for uncommitted changes
if [[ -n $(git status -s) ]]; then
    echo "⚠️  You have uncommitted changes"
    echo ""
    read -p "Do you want to continue and commit these changes? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        echo "Aborted."
        exit 0
    fi
fi

echo ""
echo "📝 Creating commit for privacy and dashboard improvements..."
echo ""

# Stage all changes
git add .

# Create detailed commit message
git commit -m "Privacy improvements and dashboard reorganization

Changes:
- 🔒 Privacy: Removed IMEI and Module Version from metrics (GDPR compliance)
- 📊 Dashboard: Added datasource selector for multi-Prometheus support
- 🎨 Dashboard: Reorganized metrics into Primary LTE and NR5G sections
- 📈 Dashboard: Added color-coded stat panels with thresholds
- 📁 Dashboard: Created clear section headers for better navigation
- 📝 Docs: Updated README to reflect privacy changes
- 📄 Docs: Added PRIVACY_CHANGES.md with detailed changelog

Privacy improvements:
- No personally identifiable information in metrics
- Device tracking not possible without IMEI
- Safe for public dashboard sharing
- GDPR compliant monitoring solution

Dashboard improvements:
- Datasource selector variable for switching Prometheus instances
- Grouped Primary LTE metrics (RSRP, RSSI, SINR, RSRQ)
- Grouped NR5G metrics (RSRP, SINR, RSRQ, Bandwidth)
- Comparison section for LTE vs 5G analysis
- Secondary carriers in dedicated section
- Color thresholds: Red (Poor) -> Orange (Fair) -> Yellow (Good) -> Green (Excellent)

All existing functionality maintained, no breaking changes to metrics or queries."

echo ""
echo "✅ Commit created successfully!"
echo ""

# Show the commit
echo "📄 Commit details:"
git log -1 --stat
echo ""

# Push to GitHub
echo "🚀 Pushing to GitHub..."
read -p "Push to remote repository now? (y/n): " PUSH

if [ "$PUSH" = "y" ]; then
    BRANCH=$(git branch --show-current)
    echo "Pushing to branch: $BRANCH"
    git push origin "$BRANCH"
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "🌐 View your repository at:"
    REMOTE_URL=$(git config --get remote.origin.url)
    if [[ $REMOTE_URL == git@* ]]; then
        # SSH format
        HTTPS_URL=$(echo $REMOTE_URL | sed 's/git@github.com:/https:\/\/github.com\//' | sed 's/\.git$//')
    else
        # HTTPS format
        HTTPS_URL=${REMOTE_URL%.git}
    fi
    echo "$HTTPS_URL"
    echo ""
    echo "📊 View commit at:"
    echo "$HTTPS_URL/commit/$(git rev-parse HEAD)"
else
    echo "⏸️  Changes committed locally but not pushed"
    echo "You can push later with: git push origin $(git branch --show-current)"
fi

echo ""
echo "================================================"
echo "Next steps:"
echo "================================================"
echo ""
echo "1. Create a new release (optional):"
echo "   git tag -a v1.1.0 -m 'Privacy improvements and dashboard reorganization'"
echo "   git push origin v1.1.0"
echo ""
echo "2. Update GitHub release notes with:"
echo "   - Privacy improvements (IMEI/Module removed)"
echo "   - Dashboard reorganization"
echo "   - Datasource selector added"
echo ""
echo "3. Consider updating:"
echo "   - Repository topics/tags"
echo "   - README badges"
echo "   - GitHub project description"
echo ""
echo "✅ Update complete!"
echo ""
