#!/bin/bash

# SEC Chatbot Deployment Script
echo "🚀 Deploying SEC Chatbot to AWS Lambda..."

# Check if required environment variables are set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY environment variable is not set"
    echo "Please set it with: export OPENAI_API_KEY=your_key_here"
    exit 1
fi

# Install serverless framework if not already installed
if ! command -v serverless &> /dev/null; then
    echo "📦 Installing Serverless Framework..."
    npm install -g serverless
    npm install -g serverless-python-requirements
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Deploy to AWS
echo "☁️ Deploying to AWS Lambda..."
serverless deploy --stage prod

echo "✅ Deployment complete!"
echo "🔗 API Gateway URL will be displayed above"
echo "📝 Don't forget to update your frontend with the new API endpoint"
