import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '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')
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "deepseek/deepseek-chat-v3.1:free"

# AWS Configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

# EDGAR API Configuration
EDGAR_BASE_URL = "https://data.sec.gov/api/xbrl/companyfacts"
EDGAR_SEARCH_URL = "https://www.sec.gov/edgar/search"

# Application Configuration
MAX_DOCUMENT_SIZE = 1000000  # 1MB limit for processing
MAX_SUMMARY_LENGTH = 2000
