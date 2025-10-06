#!/usr/bin/env python3
"""
Demo script for the SEC Chatbot.
This script demonstrates the core functionality without requiring a web interface.
"""

import os
import sys
from chatbot_service import SECChatbot

def print_banner():
    """Print a nice banner for the demo."""
    print("=" * 60)
    print("📊 SEC FILING CHATBOT DEMO")
    print("=" * 60)
    print("AI-Powered Analysis of SEC 10-K and 10-Q Filings")
    print("Built with Python, AWS Lambda, and OpenAI GPT")
    print("=" * 60)

def print_response(response):
    """Print chatbot response in a formatted way."""
    print(f"\n🤖 Bot Response:")
    print("-" * 40)
    print(response.get('response', 'No response'))
    
    if response.get('data'):
        data = response['data']
        if 'company' in data:
            company = data['company']
            print(f"\n📈 Company: {company.get('title', 'N/A')}")
            print(f"🏷️  Ticker: {company.get('ticker', 'N/A')}")
        
        if 'filing' in data:
            filing = data['filing']
            print(f"📄 Form: {filing.get('form', 'N/A')}")
            print(f"📅 Date: {filing.get('filingDate', 'N/A')}")
    
    if response.get('error'):
        print(f"\n❌ Error: {response['error']}")

def run_demo():
    """Run the interactive demo."""
    print_banner()
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("\n⚠️  WARNING: OpenAI API key not found!")
        print("   Set OPENAI_API_KEY environment variable for full functionality.")
        print("   Some features may not work without it.\n")
    
    # Initialize chatbot
    print("🚀 Initializing SEC Chatbot...")
    chatbot = SECChatbot()
    print("✅ Chatbot ready!\n")
    
    # Demo queries
    demo_queries = [
        "Search for Apple Inc",
        "Analyze Apple's latest 10-K filing",
        "What are Apple's main business risks?",
        "Summarize Apple's financial performance"
    ]
    
    print("💡 Demo Queries:")
    for i, query in enumerate(demo_queries, 1):
        print(f"   {i}. {query}")
    
    print(f"\n{'='*60}")
    print("🎯 INTERACTIVE MODE")
    print("Type your questions about SEC filings (or 'quit' to exit)")
    print("=" * 60)
    
    context = {}
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thanks for using the SEC Chatbot Demo!")
                break
            
            if not user_input:
                continue
            
            print("\n🤖 Analyzing...")
            
            # Process query
            response = chatbot.process_query(user_input, context)
            
            # Print response
            print_response(response)
            
            # Update context for follow-up questions
            if 'data' in response:
                context.update(response['data'])
            
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

def run_quick_test():
    """Run a quick test with predefined queries."""
    print_banner()
    print("🧪 Running Quick Test...\n")
    
    chatbot = SECChatbot()
    
    test_queries = [
        "Search for Microsoft",
        "Hello, how can you help me?"
    ]
    
    for query in test_queries:
        print(f"👤 Query: {query}")
        response = chatbot.process_query(query)
        print_response(response)
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_quick_test()
    else:
        run_demo()
