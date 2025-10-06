import json
import time
from typing import Dict, List, Optional
from edgar_client import EdgarClient
from llm_analyzer import LLMAnalyzer
import config

class SECChatbot:
    """Main chatbot service that integrates EDGAR API and LLM analysis."""
    
    def __init__(self):
        self.edgar_client = EdgarClient()
        # Initialize LLM analyzer with OpenRouter API key
        if config.OPENROUTER_API_KEY and config.OPENROUTER_API_KEY != "your_openrouter_api_key_here":
            self.llm_analyzer = LLMAnalyzer()
        else:
            self.llm_analyzer = None
        self.conversation_history = []
    
    def process_query(self, user_query: str, context: Dict = None) -> Dict:
        """Process user query and return appropriate response."""
        
        response = {
            "query": user_query,
            "timestamp": time.time(),
            "response": "",
            "data": {},
            "error": None
        }
        
        try:
            # Parse the query to determine intent
            intent = self._parse_intent(user_query)
            response["intent"] = intent
            
            if intent == "search_company":
                response = self._handle_company_search(user_query, response)
            elif intent == "analyze_filing":
                response = self._handle_filing_analysis(user_query, response, context)
            elif intent == "ask_question":
                response = self._handle_question(user_query, response, context)
            elif intent == "compare_companies":
                response = self._handle_comparison(user_query, response, context)
            elif intent == "get_summary":
                response = self._handle_summary(user_query, response, context)
            else:
                # If no LLM analyzer available, provide demo response
                if not self.llm_analyzer:
                    response["response"] = "🤖 **Demo Mode Active**\n\nI can help you explore SEC filings! Try these demo queries:\n\n• **Search for Apple Inc** - Find company information\n• **Analyze Microsoft's latest 10-K** - Get filing analysis\n• **What are Tesla's main business risks?** - Risk assessment\n• **Summarize Amazon's financial performance** - Financial summary\n\n*Note: This is demo mode with sample data. For real-time SEC analysis, please configure your OpenRouter API key.*"
                else:
                    response["response"] = "🤖 **AI Analysis Ready**\n\nI can help you analyze SEC filings with real AI! Try these queries:\n\n• **Search for Apple Inc** - Find company information\n• **Analyze Microsoft's latest 10-K** - Get AI-powered filing analysis\n• **What are Tesla's main business risks?** - AI risk assessment\n• **Summarize Amazon's financial performance** - AI financial summary\n\n*Powered by DeepSeek AI model via OpenRouter*"
            
            # Store in conversation history
            self.conversation_history.append(response)
            
        except Exception as e:
            response["error"] = str(e)
            response["response"] = f"I encountered an error: {str(e)}"
        
        return response
    
    def _parse_intent(self, query: str) -> str:
        """Parse user query to determine intent."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["search", "find", "look for", "company"]):
            return "search_company"
        elif any(word in query_lower for word in ["analyze", "analysis", "review", "examine"]):
            return "analyze_filing"
        elif any(word in query_lower for word in ["compare", "comparison", "vs", "versus"]):
            return "compare_companies"
        elif any(word in query_lower for word in ["summary", "summarize", "overview"]):
            return "get_summary"
        elif "?" in query or any(word in query_lower for word in ["what", "how", "why", "when", "where"]):
            return "ask_question"
        else:
            return "general"
    
    def _handle_company_search(self, query: str, response: Dict) -> Dict:
        """Handle company search requests."""
        # Extract company name from query
        company_name = self._extract_company_name(query)
        
        # If no LLM analyzer available, use demo mode
        if not self.llm_analyzer:
            return self._demo_company_search(company_name, response)
        
        if not company_name:
            response["response"] = "Please specify a company name to search for."
            return response
        
        # Search for company
        search_results = self.edgar_client.search_and_analyze(company_name)
        
        if search_results.get("error"):
            response["response"] = f"Error searching for {company_name}: {search_results['error']}"
            return response
        
        companies = search_results.get("companies_found", [])
        if not companies:
            response["response"] = f"No companies found matching '{company_name}'"
            return response
        
        # Format response
        response["response"] = f"Found {len(companies)} companies matching '{company_name}':\n\n"
        for i, company in enumerate(companies[:3], 1):
            response["response"] += f"{i}. {company['title']} (Ticker: {company['ticker']})\n"
        
        response["response"] += f"\nTo analyze {companies[0]['title']}'s latest 10-K filing, say 'analyze {companies[0]['title']}'"
        response["data"] = search_results
        
        return response
    
    def _handle_filing_analysis(self, query: str, response: Dict, context: Dict) -> Dict:
        """Handle filing analysis requests."""
        company_name = self._extract_company_name(query)
        
        if not company_name:
            response["response"] = "Please specify a company name to analyze."
            return response
        
        # If no LLM analyzer available, use demo mode
        if not self.llm_analyzer:
            return self._demo_filing_analysis(company_name, response)
        
        # Get company data and filings
        search_results = self.edgar_client.search_and_analyze(company_name, "10-K")
        
        if search_results.get("error"):
            response["response"] = f"Error analyzing {company_name}: {search_results['error']}"
            return response
        
        if not search_results.get("content"):
            response["response"] = f"No 10-K filing content found for {company_name}"
            return response
        
        # Analyze with LLM
        analysis = self.llm_analyzer.analyze_document(
            search_results["content"], 
            "comprehensive"
        )
        
        # Handle different response formats including fallbacks
        if analysis.get("error") and analysis.get("fallback"):
            # API failed but we have fallback
            response["response"] = f"Analysis of {company_name}:\n\n{analysis['fallback']}\n\n⚠️ Note: {analysis['error']}"
        elif analysis.get("error"):
            # Complete failure
            response["response"] = f"Analysis failed for {company_name}: {analysis['error']}"
        else:
            # Successful analysis - format response
            response["response"] = self._format_analysis_response(analysis, company_name)
        
        response["data"] = {
            "company": search_results.get("selected_company"),
            "filing": search_results.get("selected_filing"),
            "analysis": analysis
        }
        
        return response
    
    def _handle_question(self, query: str, response: Dict, context: Dict) -> Dict:
        """Handle specific questions about filings."""
        if not context or not context.get("content"):
            response["response"] = "Please first search for and analyze a company's filing before asking questions."
            return response
        
        answer = self.llm_analyzer.answer_question(context["content"], query)
        response["response"] = answer
        response["data"] = {"question": query, "answer": answer}
        
        return response
    
    def _handle_summary(self, query: str, response: Dict, context: Dict) -> Dict:
        """Handle summary requests."""
        if not context or not context.get("content"):
            response["response"] = "Please first search for and analyze a company's filing before requesting a summary."
            return response
        
        summary = self.llm_analyzer.generate_summary(context["content"])
        response["response"] = f"**Executive Summary:**\n\n{summary}"
        response["data"] = {"summary": summary}
        
        return response
    
    def _handle_comparison(self, query: str, response: Dict, context: Dict) -> Dict:
        """Handle company comparison requests."""
        # This would require multiple company analyses
        response["response"] = "Company comparison feature requires analyzing multiple companies. Please analyze individual companies first, then I can help compare them."
        return response
    
    def _extract_company_name(self, query: str) -> str:
        """Extract company name from query."""
        # Simple extraction - look for words after common patterns
        query_lower = query.lower()
        
        patterns = [
            "analyze ", "search for ", "find ", "look for ", "company ",
            "analyze ", "review ", "examine "
        ]
        
        for pattern in patterns:
            if pattern in query_lower:
                start_idx = query_lower.find(pattern) + len(pattern)
                company_part = query[start_idx:].strip()
                # Take first few words as company name
                words = company_part.split()[:3]
                return " ".join(words)
        
        # If no pattern found, return the query itself (cleaned)
        return query.strip()
    
    def _format_analysis_response(self, analysis: Dict, company_name: str) -> str:
        """Format LLM analysis into a readable response."""
        if analysis.get("format") == "text":
            return f"**Analysis of {company_name}:**\n\n{analysis.get('raw_analysis', 'No analysis available')}"
        
        response = f"**Comprehensive Analysis of {company_name}:**\n\n"
        
        if "executive_summary" in analysis:
            response += f"**Executive Summary:**\n{analysis['executive_summary']}\n\n"
        
        if "financial_highlights" in analysis:
            financial = analysis["financial_highlights"]
            response += f"**Financial Highlights:**\n"
            if isinstance(financial, dict):
                for key, value in financial.items():
                    if key != "key_metrics":
                        response += f"• {key.replace('_', ' ').title()}: {value}\n"
                if "key_metrics" in financial:
                    response += f"• Key Metrics: {', '.join(financial['key_metrics'])}\n"
            response += "\n"
        
        if "business_risks" in analysis:
            response += f"**Key Business Risks:**\n"
            for risk in analysis["business_risks"][:3]:
                response += f"• {risk}\n"
            response += "\n"
        
        if "growth_opportunities" in analysis:
            response += f"**Growth Opportunities:**\n"
            for opp in analysis["growth_opportunities"][:3]:
                response += f"• {opp}\n"
            response += "\n"
        
        if "key_insights" in analysis:
            response += f"**Key Insights:**\n"
            for insight in analysis["key_insights"][:3]:
                response += f"• {insight}\n"
            response += "\n"
        
        if "investment_recommendation" in analysis:
            response += f"**Investment Outlook:**\n{analysis['investment_recommendation']}\n\n"
        
        if "confidence_score" in analysis:
            response += f"*Analysis Confidence: {analysis['confidence_score']}%*"
        
        return response
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history."""
        return self.conversation_history
    
    def _demo_company_search(self, company_name: str, response: Dict) -> Dict:
        """Demo mode company search with sample data."""
        if not company_name:
            response["response"] = "Please specify a company name to search for."
            return response
        
        # Enhanced demo data with more companies
        demo_companies = {
            "apple": {
                "cik": "0000320193",
                "ticker": "AAPL",
                "title": "Apple Inc.",
                "description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.",
                "market_cap": "$3.2T",
                "employees": "164,000",
                "founded": "1976"
            },
            "microsoft": {
                "cik": "0000789019", 
                "ticker": "MSFT",
                "title": "Microsoft Corporation",
                "description": "Microsoft Corporation develops, licenses, and supports software, services, devices, and solutions worldwide.",
                "market_cap": "$2.8T",
                "employees": "221,000",
                "founded": "1975"
            },
            "tesla": {
                "cik": "0001318605",
                "ticker": "TSLA", 
                "title": "Tesla, Inc.",
                "description": "Tesla, Inc. designs, develops, manufactures, leases, and sells electric vehicles, and energy generation and storage systems.",
                "market_cap": "$800B",
                "employees": "127,855",
                "founded": "2003"
            },
            "amazon": {
                "cik": "0001018724",
                "ticker": "AMZN",
                "title": "Amazon.com, Inc.",
                "description": "Amazon.com, Inc. engages in the retail sale of consumer products and subscriptions in North America and internationally.",
                "market_cap": "$1.5T",
                "employees": "1.5M",
                "founded": "1994"
            },
            "google": {
                "cik": "0001652044",
                "ticker": "GOOGL",
                "title": "Alphabet Inc.",
                "description": "Alphabet Inc. provides online advertising services in the United States, Europe, the Middle East, Africa, the Asia-Pacific, Canada, and Latin America.",
                "market_cap": "$1.7T",
                "employees": "190,000",
                "founded": "1998"
            },
            "meta": {
                "cik": "0001326801",
                "ticker": "META",
                "title": "Meta Platforms, Inc.",
                "description": "Meta Platforms, Inc. develops products that help people connect and share with friends and family through mobile devices, personal computers, virtual reality headsets, and wearables worldwide.",
                "market_cap": "$800B",
                "employees": "77,000",
                "founded": "2004"
            }
        }
        
        # Find matching company
        company_key = None
        for key, company in demo_companies.items():
            if key in company_name.lower() or company_name.lower() in key:
                company_key = key
                break
        
        if company_key:
            company = demo_companies[company_key]
            response["response"] = f"🏢 **{company['title']}** ({company['ticker']})\n\n📊 **Company Overview:**\n{company['description']}\n\n📈 **Key Metrics:**\n• Market Cap: {company['market_cap']}\n• Employees: {company['employees']}\n• Founded: {company['founded']}\n• CIK: {company['cik']}\n\n💡 **Next Steps:**\nTry asking: \"Analyze {company['title']}'s latest 10-K\" for detailed financial analysis.\n\n*Note: This is demo data. For real-time SEC data, please configure your OpenRouter API key.*"
            response["data"] = {
                "company": company,
                "demo_mode": True
            }
        else:
            response["response"] = f"🔍 **Company Search Results**\n\nI couldn't find '{company_name}' in our demo database.\n\n**Available Demo Companies:**\n• Apple Inc. (AAPL)\n• Microsoft Corporation (MSFT)\n• Tesla, Inc. (TSLA)\n• Amazon.com, Inc. (AMZN)\n• Alphabet Inc. (GOOGL)\n• Meta Platforms, Inc. (META)\n\nTry searching for one of these companies!\n\n*Note: This is demo mode. For real company searches, please configure your OpenRouter API key.*"
        
        return response
    
    def _demo_filing_analysis(self, company_name: str, response: Dict) -> Dict:
        """Demo mode filing analysis with sample data."""
        # Enhanced demo analysis data
        demo_analyses = {
            "apple": {
                "company": {"title": "Apple Inc.", "ticker": "AAPL"},
                "filing": {"form": "10-K", "filingDate": "2023-10-27"},
                "analysis": {
                    "executive_summary": "Apple Inc. continues to demonstrate strong financial performance with record revenue in fiscal 2023, driven by robust iPhone sales and growing services revenue.",
                    "financial_highlights": {
                        "revenue": "$383.3 billion (up 2.8% YoY)",
                        "profitability": "Net income of $97.0 billion with 25.3% net margin",
                        "key_metrics": ["iPhone revenue: $200.6B", "Services revenue: $85.2B", "Mac revenue: $29.4B"]
                    },
                    "business_risks": [
                        "Intense competition in smartphone and technology markets",
                        "Dependence on third-party manufacturers and suppliers",
                        "Regulatory challenges in key markets"
                    ],
                    "growth_opportunities": [
                        "Expansion of services ecosystem",
                        "Growth in emerging markets",
                        "Innovation in augmented reality and autonomous systems"
                    ],
                    "investment_recommendation": "Strong buy - Apple's ecosystem moat, strong cash generation, and innovation pipeline support continued growth.",
                    "confidence_score": 88
                }
            },
            "microsoft": {
                "company": {"title": "Microsoft Corporation", "ticker": "MSFT"},
                "filing": {"form": "10-K", "filingDate": "2023-07-28"},
                "analysis": {
                    "executive_summary": "Microsoft delivered strong growth across all business segments, with Azure and Office 365 driving significant revenue increases.",
                    "financial_highlights": {
                        "revenue": "$211.9 billion (up 7.4% YoY)",
                        "profitability": "Net income of $72.4 billion with 34.2% net margin",
                        "key_metrics": ["Azure revenue growth: 27%", "Office 365 revenue: $44.8B", "LinkedIn revenue: $15.2B"]
                    },
                    "business_risks": [
                        "Competition in cloud computing market",
                        "Cybersecurity threats and data privacy concerns",
                        "Dependence on enterprise customers"
                    ],
                    "growth_opportunities": [
                        "AI and machine learning integration",
                        "Expansion of cloud services globally",
                        "Gaming and entertainment growth"
                    ],
                    "investment_recommendation": "Buy - Microsoft's cloud leadership and AI integration position it well for continued growth.",
                    "confidence_score": 85
                }
            },
            "tesla": {
                "company": {"title": "Tesla, Inc.", "ticker": "TSLA"},
                "filing": {"form": "10-K", "filingDate": "2024-01-26"},
                "analysis": {
                    "executive_summary": "Tesla continues to lead the electric vehicle revolution with strong delivery growth and expanding energy business.",
                    "financial_highlights": {
                        "revenue": "$96.8 billion (up 19% YoY)",
                        "profitability": "Net income of $15.0 billion with 15.5% net margin",
                        "key_metrics": ["Vehicle deliveries: 1.8M", "Energy storage: 14.7 GWh", "Supercharger stations: 5,952"]
                    },
                    "business_risks": [
                        "Intense competition in EV market",
                        "Regulatory changes affecting autonomous driving",
                        "Supply chain disruptions"
                    ],
                    "growth_opportunities": [
                        "Expansion of Full Self-Driving technology",
                        "Growth in energy storage business",
                        "International market expansion"
                    ],
                    "investment_recommendation": "Hold - Strong market position but high valuation and execution risks.",
                    "confidence_score": 75
                }
            },
            "amazon": {
                "company": {"title": "Amazon.com, Inc.", "ticker": "AMZN"},
                "filing": {"form": "10-K", "filingDate": "2024-02-02"},
                "analysis": {
                    "executive_summary": "Amazon's diversified business model continues to drive growth across e-commerce, cloud computing, and digital services.",
                    "financial_highlights": {
                        "revenue": "$574.8 billion (up 12% YoY)",
                        "profitability": "Net income of $30.4 billion with 5.3% net margin",
                        "key_metrics": ["AWS revenue: $90.8B", "Prime members: 200M+", "Marketplace GMV: $500B+"]
                    },
                    "business_risks": [
                        "Intense competition in cloud computing",
                        "Regulatory scrutiny of market dominance",
                        "Labor and supply chain costs"
                    ],
                    "growth_opportunities": [
                        "AWS expansion in enterprise and AI",
                        "International e-commerce growth",
                        "Advertising and media services"
                    ],
                    "investment_recommendation": "Buy - Strong competitive moats and multiple growth drivers.",
                    "confidence_score": 82
                }
            }
        }
        
        # Find matching company
        company_key = None
        for key in demo_analyses.keys():
            if key in company_name.lower() or company_name.lower() in key:
                company_key = key
                break
        
        if company_key:
            analysis_data = demo_analyses[company_key]
            response["response"] = f"📊 **Analysis of {analysis_data['company']['title']} ({analysis_data['company']['ticker']})**\n\n{analysis_data['analysis']['executive_summary']}\n\n*Note: This is demo analysis data. For real-time SEC filing analysis, please configure your OpenRouter API key.*"
            response["data"] = analysis_data
        else:
            response["response"] = f"I can provide demo analysis for Apple or Microsoft. Try 'Analyze Apple's latest 10-K' or 'Analyze Microsoft's latest 10-K'.\n\n*Note: This is demo mode. For real filing analysis, please configure your OpenRouter API key.*"
        
        return response
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
