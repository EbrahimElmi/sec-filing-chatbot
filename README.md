# 📊 SEC Filing Chatbot

An AI-powered chatbot that analyzes SEC 10-K/10-Q filings using real-time data from the SEC EDGAR API and OpenRouter's DeepSeek model for intelligent analysis.

## 🚀 Features

- **Real-time SEC Data Retrieval**: Integrated EDGAR API for accessing 10-K and 10-Q filings
- **AI-Powered Analysis**: Leverages OpenRouter DeepSeek model for intelligent document analysis
- **Comprehensive Insights**: Extracts financial highlights, business risks, growth opportunities, and investment recommendations
- **Interactive Web Interface**: Beautiful Streamlit-based chat interface with clean UI
- **Rate Limit Handling**: Smart retry logic with exponential backoff for API reliability
- **Fallback Analysis**: Graceful degradation when APIs are unavailable
- **Production-Ready**: Includes proper error handling, logging, and deployment configurations

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │───▶│  Python Backend │───▶│  OpenRouter     │
│   (Frontend)    │    │  (Local/Cloud)  │    │  DeepSeek AI    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   SEC EDGAR     │
                       │   (Data Source) │
                       └─────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: Python 3.9, Streamlit
- **Frontend**: Streamlit, HTML/CSS
- **AI/ML**: OpenRouter DeepSeek, Prompt Engineering
- **Data Source**: SEC EDGAR API
- **Deployment**: Streamlit Cloud (free hosting)
- **Infrastructure**: Git version control, Environment variables

## 📋 Prerequisites

- Python 3.9+
- OpenRouter API Key
- Git (for version control)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/YOUR_USERNAME/sec-filing-chatbot.git
cd sec-filing-chatbot
```

### 2. Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env.example .env
```

### 3. Configure API Keys

Edit `.env` file and add your OpenRouter API key:

```bash
OPENROUTER_API_KEY=your_actual_api_key_here
```

### 4. Run Locally

```bash
streamlit run app.py --server.port 8505
```

Visit: http://localhost:8505

### 5. Deploy to Streamlit Cloud

1. Push to GitHub
2. Go to https://share.streamlit.io
3. Connect your repository
4. Add environment variables in Streamlit Cloud dashboard
5. Deploy!

## 💬 Usage Examples

### Company Search
```
"Search for Apple Inc"
"Find Microsoft Corporation"
"Look for Tesla Inc"
```

### Filing Analysis
```
"Analyze Apple's latest 10-K filing"
"Review Microsoft's financial performance"
"Examine Tesla's business risks"
```

### Specific Questions
```
"What are Apple's main revenue sources?"
"How has Microsoft's profitability changed?"
"What risks does Tesla face in the EV market?"
```

### Summaries
```
"Summarize Amazon's latest 10-K"
"Give me an overview of Google's financials"
```

## 🔧 API Endpoints

### POST /chat
Send chat messages to the chatbot.

**Request:**
```json
{
  "query": "Analyze Apple's latest 10-K",
  "context": {}
}
```

**Response:**
```json
{
  "query": "Analyze Apple's latest 10-K",
  "response": "**Comprehensive Analysis of Apple Inc:**...",
  "data": {
    "company": {...},
    "filing": {...},
    "analysis": {...}
  },
  "timestamp": 1234567890
}
```

### GET /health
Health check endpoint.

## 📊 Analysis Capabilities

The chatbot provides comprehensive analysis including:

- **Executive Summary**: High-level company overview
- **Financial Highlights**: Revenue, profitability, key metrics
- **Business Risks**: Operational, market, regulatory risks
- **Growth Opportunities**: Market expansion, new products
- **Investment Recommendations**: AI-powered outlook
- **Confidence Scores**: Analysis reliability metrics

## 🏗️ Project Structure

```
genai-sec-chatbot/
├── app.py                 # Streamlit frontend
├── chatbot_service.py     # Main chatbot logic
├── edgar_client.py        # SEC EDGAR API integration
├── llm_analyzer.py        # OpenAI LLM integration
├── lambda_function.py     # AWS Lambda handler
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── serverless.yml        # Serverless deployment config
├── deploy.sh            # Deployment script
└── README.md            # This file
```

## 🔒 Security & Best Practices

- Environment variables for sensitive data
- CORS configuration for web security
- Error handling and logging
- Rate limiting considerations
- Input validation and sanitization

## 📈 Performance Optimizations

- Document content truncation for token limits
- Caching of company search results
- Efficient HTML parsing with BeautifulSoup
- Streamlit session state management
- AWS Lambda cold start optimization

## 🚀 Deployment Options

### Option 1: AWS Lambda (Recommended)
- Serverless and scalable
- Cost-effective for variable traffic
- Automatic scaling
- Integrated with AWS services

### Option 2: Local Development
- Perfect for testing and development
- No AWS costs
- Direct API integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review error logs in CloudWatch (if deployed)
3. Test with example queries
4. Verify API keys and permissions

## 🎯 Future Enhancements

- [ ] Support for additional SEC forms (8-K, 10-Q)
- [ ] Multi-company comparison features
- [ ] Historical trend analysis
- [ ] Export analysis to PDF/Excel
- [ ] Integration with financial data APIs
- [ ] Advanced visualization dashboards
- [ ] Real-time market data integration

---

**Built with using Python, AWS Lambda, and Deepseek API**
