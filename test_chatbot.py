#!/usr/bin/env python3
"""
Test script for the SEC Chatbot functionality.
Run this to verify all components are working correctly.
"""

import os
import sys
from chatbot_service import SECChatbot
from edgar_client import EdgarClient
from llm_analyzer import LLMAnalyzer

def test_edgar_client():
    """Test EDGAR API client functionality."""
    print("🔍 Testing EDGAR Client...")
    
    client = EdgarClient()
    
    # Test company search
    companies = client.search_company("Apple")
    if companies:
        print(f"✅ Found {len(companies)} companies matching 'Apple'")
        print(f"   First result: {companies[0]['title']}")
    else:
        print("❌ No companies found for 'Apple'")
        return False
    
    # Test filing retrieval
    if companies:
        cik = companies[0]['cik']
        filings = client.get_recent_filings(cik, "10-K")
        if filings:
            print(f"✅ Found {len(filings)} 10-K filings")
        else:
            print("❌ No 10-K filings found")
            return False
    
    return True

def test_llm_analyzer():
    """Test LLM analyzer functionality."""
    print("🤖 Testing LLM Analyzer...")
    
    # Check if OpenAI API key is available
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OpenAI API key not found. Skipping LLM tests.")
        return True
    
    analyzer = LLMAnalyzer()
    
    # Test with sample content
    sample_content = """
    Apple Inc. reported strong financial performance for the fiscal year 2023.
    Revenue increased by 8% year-over-year to $394.3 billion.
    The company's services segment showed significant growth.
    Key risks include supply chain disruptions and competitive pressures.
    """
    
    # Test summary generation
    summary = analyzer.generate_summary(sample_content)
    if summary and len(summary) > 50:
        print("✅ Summary generation working")
    else:
        print("❌ Summary generation failed")
        return False
    
    # Test question answering
    answer = analyzer.answer_question(sample_content, "What was Apple's revenue?")
    if answer and len(answer) > 20:
        print("✅ Question answering working")
    else:
        print("❌ Question answering failed")
        return False
    
    return True

def test_chatbot_service():
    """Test the main chatbot service."""
    print("💬 Testing Chatbot Service...")
    
    chatbot = SECChatbot()
    
    # Test company search query
    response = chatbot.process_query("Search for Apple Inc")
    if response.get('response') and not response.get('error'):
        print("✅ Company search query working")
    else:
        print(f"❌ Company search failed: {response.get('error', 'Unknown error')}")
        return False
    
    # Test general query
    response = chatbot.process_query("Hello, how can you help me?")
    if response.get('response'):
        print("✅ General query handling working")
    else:
        print("❌ General query handling failed")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🚀 Starting SEC Chatbot Tests...\n")
    
    tests = [
        ("EDGAR Client", test_edgar_client),
        ("LLM Analyzer", test_llm_analyzer),
        ("Chatbot Service", test_chatbot_service)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        try:
            if test_func():
                print(f"✅ {test_name} test PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test FAILED with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The chatbot is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
