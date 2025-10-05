#!/bin/bash

# AWS Infrastructure Reporting Tool - GitHub Pages Setup Script
# This script helps you set up automated GitHub Pages deployment

set -e

echo "🚀 Setting up GitHub Pages for AWS Infrastructure Reporting Tool"
echo "================================================================="

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository. Please run this from the project root."
    exit 1
fi

# Check if GitHub remote exists
if ! git remote get-url origin >/dev/null 2>&1; then
    echo "❌ Error: No GitHub remote found. Please add your GitHub repository as origin."
    echo "   Example: git remote add origin https://github.com/yourusername/infra.git"
    exit 1
fi

echo "✅ Git repository detected"

# Check if GitHub CLI is available
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI detected"
    
    # Check if user is authenticated
    if gh auth status >/dev/null 2>&1; then
        echo "✅ GitHub CLI authenticated"
        
        # Get repository info
        REPO_OWNER=$(gh repo view --json owner --jq '.owner.login')
        REPO_NAME=$(gh repo view --json name --jq '.name')
        
        echo "📋 Repository: $REPO_OWNER/$REPO_NAME"
        echo ""
        echo "🔧 Next steps:"
        echo "1. Add AWS credentials as GitHub secrets:"
        echo "   - Go to: https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions"
        echo "   - Add 'AWS_ACCESS_KEY_ID'"
        echo "   - Add 'AWS_SECRET_ACCESS_KEY'"
        echo ""
        echo "2. Enable GitHub Pages:"
        echo "   - Go to: https://github.com/$REPO_OWNER/$REPO_NAME/settings/pages"
        echo "   - Set Source to 'GitHub Actions'"
        echo ""
        echo "3. Test the workflow:"
        echo "   - Go to: https://github.com/$REPO_OWNER/$REPO_NAME/actions"
        echo "   - Run 'Deploy AWS Cost Report to GitHub Pages' workflow"
        echo ""
        echo "4. Access your reports:"
        echo "   - URL: https://$REPO_OWNER.github.io/$REPO_NAME"
        echo ""
        echo "📝 The workflow will run daily at 2 AM UTC and can be triggered manually."
        
    else
        echo "⚠️  GitHub CLI not authenticated. Please run: gh auth login"
    fi
else
    echo "⚠️  GitHub CLI not found. Manual setup required:"
    echo ""
    echo "🔧 Manual setup steps:"
    echo "1. Add AWS credentials as GitHub secrets:"
    echo "   - Go to your repository Settings → Secrets and variables → Actions"
    echo "   - Add 'AWS_ACCESS_KEY_ID'"
    echo "   - Add 'AWS_SECRET_ACCESS_KEY'"
    echo ""
    echo "2. Enable GitHub Pages:"
    echo "   - Go to Settings → Pages"
    echo "   - Set Source to 'GitHub Actions'"
    echo ""
    echo "3. Test the workflow:"
    echo "   - Go to Actions tab"
    echo "   - Run 'Deploy AWS Cost Report to GitHub Pages' workflow"
    echo ""
    echo "4. Access your reports:"
    echo "   - URL: https://yourusername.github.io/infra"
fi

echo ""
echo "✅ Setup script completed!"
echo "📚 For more details, see README.md"
