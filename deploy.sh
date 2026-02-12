#!/bin/bash

# Deployment Script for Enhanced Human-Agent Data Analysis Tool
# This script helps deploy the application to Streamlit Community Cloud

echo "🚀 Enhanced Human-Agent Data Analysis Tool - Deployment Helper"
echo "=============================================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the project root."
    exit 1
fi

echo "✅ Project structure validated"

# Check if secrets are configured
if [ ! -f ".streamlit/secrets.toml" ]; then
    echo "⚠️  Warning: .streamlit/secrets.toml not found"
    echo "   Make sure to configure your OpenAI API key for deployment"
else
    echo "✅ Secrets configuration found"
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found"
    exit 1
else
    echo "✅ Requirements file found"
fi

echo ""
echo "📋 Deployment Steps for Streamlit Community Cloud:"
echo "1. Push this repository to GitHub"
echo "2. Go to https://share.streamlit.io/"
echo "3. Click 'New app' and connect your GitHub account"
echo "4. Select this repository and main branch"
echo "5. Set main file path to: app.py"
echo "6. Click 'Deploy'"
echo ""
echo "🔑 Your API key is already configured in .streamlit/secrets.toml"
echo "   For production, consider using Streamlit's secret management"
echo ""

# Optional: Test run locally
read -p "Do you want to test the application locally? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧪 Testing application locally..."
    if command -v streamlit &> /dev/null; then
        streamlit run app.py --server.port 8501
    else
        echo "❌ Streamlit not found. Install with: pip install streamlit"
    fi
fi

echo "🎉 Deployment helper complete!"
