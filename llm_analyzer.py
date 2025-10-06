import requests
from typing import Dict, List, Optional
import config
import json

class LLMAnalyzer:
    """LLM-powered analyzer for SEC filings using OpenRouter DeepSeek model."""
    
    def __init__(self):
        self.api_key = config.OPENROUTER_API_KEY
        self.base_url = config.OPENROUTER_BASE_URL
        self.model = config.OPENROUTER_MODEL
    
    def create_analysis_prompt(self, document_content: str, analysis_type: str = "comprehensive") -> str:
        """Create a structured prompt for document analysis."""
        
        if analysis_type == "comprehensive":
            prompt = f"""
            Analyze this SEC filing and provide a concise summary in plain text (not JSON).
            
            Document Content:
            {document_content[:4000]}
            
            Give me a simple, readable response with:
            1. Brief company overview (2-3 sentences)
            2. Main financial highlights (2-3 key points)
            3. Top 2-3 business risks
            4. Top 2-3 growth opportunities
            5. Investment outlook (1-2 sentences)
            
            Keep it concise and easy to read. No JSON formatting.
            """
        
        elif analysis_type == "financial":
            prompt = f"""
            Extract and analyze financial information from this SEC filing:
            
            {document_content[:6000]}
            
            Return JSON format:
            {{
                "revenue_analysis": "Revenue trends and breakdown",
                "profitability_metrics": "Profit margins and profitability analysis",
                "balance_sheet_highlights": "Key balance sheet items",
                "cash_flow_insights": "Cash flow analysis",
                "financial_ratios": {{"ratio1": "value1", "ratio2": "value2"}},
                "year_over_year_changes": "Key YoY changes"
            }}
            """
        
        elif analysis_type == "risks":
            prompt = f"""
            Identify and analyze risk factors from this SEC filing:
            
            {document_content[:6000]}
            
            Return JSON format:
            {{
                "operational_risks": ["risk1", "risk2"],
                "market_risks": ["risk1", "risk2"],
                "regulatory_risks": ["risk1", "risk2"],
                "financial_risks": ["risk1", "risk2"],
                "risk_mitigation": "How company addresses risks",
                "risk_severity": "Overall risk assessment"
            }}
            """
        
        return prompt
    
    def analyze_document(self, document_content: str, analysis_type: str = "comprehensive") -> Dict:
        """Analyze SEC filing document using OpenRouter DeepSeek model with retry logic."""
        import time
        
        if not document_content:
            return {"error": "No document content provided"}
        
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                prompt = self.create_analysis_prompt(document_content, analysis_type)
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:8501",
                    "X-Title": "SEC Filing Chatbot"
                }
                
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful financial analyst. Provide clear, concise answers about SEC filings. Use simple language and avoid complex formatting."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.3
                }
                
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    # Try to parse JSON response
                    try:
                        analysis_result = json.loads(content)
                        analysis_result["analysis_type"] = analysis_type
                        analysis_result["model_used"] = self.model
                        return analysis_result
                    except json.JSONDecodeError:
                        # If JSON parsing fails, return the raw content
                        return {
                            "raw_analysis": content,
                            "analysis_type": analysis_type,
                            "model_used": self.model,
                            "format": "text"
                        }
                        
                elif response.status_code == 429:
                    # Rate limit hit - wait and retry
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                        print(f"Rate limit hit, waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                        time.sleep(wait_time)
                        continue
                    else:
                        return {
                            "error": "API rate limit exceeded. Please try again in a few minutes.",
                            "fallback": self._generate_fallback_analysis(document_content, analysis_type)
                        }
                else:
                    return {
                        "error": f"API request failed with status {response.status_code}: {response.text}",
                        "fallback": self._generate_fallback_analysis(document_content, analysis_type)
                    }
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Request failed, retrying in {retry_delay} seconds: {str(e)}")
                    time.sleep(retry_delay)
                    continue
                else:
                    return {
                        "error": f"Analysis failed: {str(e)}",
                        "fallback": self._generate_fallback_analysis(document_content, analysis_type)
                    }
        
        return {
            "error": "Max retries exceeded",
            "fallback": self._generate_fallback_analysis(document_content, analysis_type)
        }
    
    def _generate_fallback_analysis(self, document_content: str, analysis_type: str) -> str:
        """Generate a basic analysis when API is unavailable."""
        content_preview = document_content[:1000] if document_content else "No content available"
        
        if analysis_type == "comprehensive":
            return f"""
**Company Analysis (Fallback Mode)**

Based on the available SEC filing data:

**Business Overview:**
The company appears to be operating in the market with various business segments and operations as detailed in their SEC filings.

**Key Information:**
- Filing contains standard SEC reporting requirements
- Company maintains compliance with regulatory standards
- Financial data and business operations are documented

**Note:** This is a basic analysis due to API limitations. For detailed analysis, please try again later when the service is available.

**Content Preview:** {content_preview}...
            """
        else:
            return f"Basic analysis unavailable due to API limitations. Content preview: {content_preview}..."
    
    def generate_summary(self, document_content: str, max_length: int = 500) -> str:
        """Generate a concise summary of the document."""
        
        prompt = f"""
        Summarize this SEC filing in 2-3 short paragraphs:
        
        {document_content[:3000]}
        
        Keep it simple and focus on the main points about the company and its financials.
        """
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "SEC Filing Chatbot"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a business analyst creating executive summaries. Be concise and focus on key insights."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 300,
                "temperature": 0.3
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result["choices"][0]["message"]["content"].strip()
            
        except Exception as e:
            return f"Summary generation failed: {str(e)}"
    
    def answer_question(self, document_content: str, question: str) -> str:
        """Answer specific questions about the document."""
        
        prompt = f"""
        Based on the following SEC filing document, answer this question: {question}
        
        Document Content:
        {document_content[:6000]}
        
        Provide a clear, accurate answer based only on the information in the document.
        If the information is not available in the document, state that clearly.
        Include relevant data points and quotes when possible.
        """
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "SEC Filing Chatbot"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a helpful financial analyst. Answer questions about SEC filings clearly and concisely."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.2
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result["choices"][0]["message"]["content"].strip()
            
        except Exception as e:
            return f"Question answering failed: {str(e)}"
    
    def compare_companies(self, documents: List[Dict]) -> Dict:
        """Compare multiple company filings."""
        
        if len(documents) < 2:
            return {"error": "At least 2 documents required for comparison"}
        
        doc_summaries = []
        for i, doc in enumerate(documents):
            doc_summaries.append(f"Company {i+1} ({doc.get('company_name', 'Unknown')}):\n{doc.get('content', '')[:2000]}")
        
        prompt = f"""
        Compare the following SEC filings and provide a comparative analysis:
        
        {chr(10).join(doc_summaries)}
        
        Return JSON format:
        {{
            "comparison_summary": "Overall comparison",
            "financial_comparison": "Financial metrics comparison",
            "risk_comparison": "Risk factors comparison",
            "growth_comparison": "Growth prospects comparison",
            "recommendations": ["recommendation1", "recommendation2"],
            "winner": "Company with better prospects"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial analyst comparing companies. Provide objective, data-driven comparisons."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"raw_comparison": content}
                
        except Exception as e:
            return {"error": f"Comparison failed: {str(e)}"}
