#!/bin/bash

# SEC Chatbot Setup Script
echo "🚀 Setting up SEC Filing Chatbot..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python $python_version detected"
else
    echo "❌ Python 3.9+ required. Current version: $python_version"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check for required environment variables
echo "🔑 Checking environment variables..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set. Create a .env file with:"
    echo "   OPENAI_API_KEY=your_openai_api_key_here"
    echo "   AWS_ACCESS_KEY_ID=your_aws_access_key_here"
    echo "   AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here"
    echo "   AWS_REGION=us-east-1"
fi

# Run tests
echo "🧪 Running tests..."
python test_chatbot.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Quick Start Options:"
echo "   1. Run demo:        python demo.py"
echo "   2. Run web app:     streamlit run app.py"
echo "   3. Deploy to AWS:   ./deploy.sh"
echo ""
echo "📚 For more information, see README.md"
