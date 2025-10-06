import requests
import json
import time
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import config

class EdgarClient:
    """Client for interacting with SEC EDGAR API to retrieve 10-K and 10-Q filings."""
    
    def __init__(self):
        self.base_url = config.EDGAR_BASE_URL
        self.search_url = config.EDGAR_SEARCH_URL
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GenAI-SEC-Chatbot/1.0 (contact@example.com)',
            'Accept': 'application/json'
        })
    
    def search_company(self, company_name: str) -> List[Dict]:
        """Search for a company by name and return basic information."""
        try:
            # Use SEC's company tickers endpoint
            tickers_url = "https://www.sec.gov/files/company_tickers.json"
            response = self.session.get(tickers_url)
            response.raise_for_status()
            
            tickers_data = response.json()
            results = []
            
            # First, try exact matches
            for entry in tickers_data.values():
                title = entry.get('title', '').lower()
                ticker = entry.get('ticker', '').lower()
                search_term = company_name.lower()
                
                # Check for exact matches first
                if search_term in title or search_term == ticker:
                    results.append({
                        'cik': str(entry['cik_str']).zfill(10),
                        'ticker': entry['ticker'],
                        'title': entry['title'],
                        'match_score': 100 if search_term == ticker else 90
                    })
            
            # If no exact matches, try partial matches
            if not results:
                for entry in tickers_data.values():
                    title = entry.get('title', '').lower()
                    search_words = search_term.split()
                    
                    # Check if any search words are in the title
                    if any(word in title for word in search_words if len(word) > 2):
                        results.append({
                            'cik': str(entry['cik_str']).zfill(10),
                            'ticker': entry['ticker'],
                            'title': entry['title'],
                            'match_score': 70
                        })
            
            # Sort by match score and return top 5
            results.sort(key=lambda x: x.get('match_score', 0), reverse=True)
            return results[:5]
            
        except Exception as e:
            print(f"Error searching for company: {e}")
            return []
    
    def get_company_overview(self, cik: str) -> Optional[Dict]:
        """Get comprehensive company overview including recent filings and key metrics."""
        try:
            # Get company submissions data
            submissions_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            response = self.session.get(submissions_url)
            response.raise_for_status()
            
            data = response.json()
            
            # Get recent filings for more context
            recent_filings = data.get('filings', {}).get('recent', {})
            forms = recent_filings.get('form', [])
            filing_dates = recent_filings.get('filingDate', [])
            accession_numbers = recent_filings.get('accessionNumber', [])
            
            # Find latest 10-K and 10-Q filings
            latest_10k = None
            latest_10q = None
            
            for i, form in enumerate(forms):
                if form == '10-K' and not latest_10k:
                    latest_10k = {
                        'form': form,
                        'date': filing_dates[i] if i < len(filing_dates) else '',
                        'accession': accession_numbers[i] if i < len(accession_numbers) else ''
                    }
                elif form == '10-Q' and not latest_10q:
                    latest_10q = {
                        'form': form,
                        'date': filing_dates[i] if i < len(filing_dates) else '',
                        'accession': accession_numbers[i] if i < len(accession_numbers) else ''
                    }
            
            # Extract comprehensive information
            overview = {
                'name': data.get('name', ''),
                'ticker': data.get('tickers', [''])[0] if data.get('tickers') else '',
                'sic': data.get('sic', ''),
                'sic_description': data.get('sicDescription', ''),
                'state': data.get('stateOfIncorporation', ''),
                'fiscal_year_end': data.get('fiscalYearEnd', ''),
                'business_address': data.get('addresses', {}).get('business', {}),
                'mailing_address': data.get('addresses', {}).get('mailing', {}),
                'recent_filings_count': len(forms),
                'latest_10k': latest_10k,
                'latest_10q': latest_10q,
                'entity_type': data.get('entityType', ''),
                'phone': data.get('phone', ''),
                'website': data.get('website', ''),
                'former_names': data.get('formerNames', [])
            }
            
            return overview
            
        except Exception as e:
            print(f"Error getting company overview: {e}")
            return None
    
    def get_company_facts(self, cik: str) -> Optional[Dict]:
        """Get company facts data for a given CIK."""
        try:
            url = f"{self.base_url}/CIK{cik}.json"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting company facts: {e}")
            return None
    
    def get_recent_filings(self, cik: str, form_type: str = "10-K") -> List[Dict]:
        """Get recent filings for a company."""
        try:
            # Use SEC's submissions endpoint
            submissions_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            response = self.session.get(submissions_url)
            response.raise_for_status()
            
            data = response.json()
            filings = []
            
            if 'filings' in data and 'recent' in data['filings']:
                recent = data['filings']['recent']
                
                for i, form in enumerate(recent.get('form', [])):
                    if form_type in form:
                        filing = {
                            'form': form,
                            'filingDate': recent.get('filingDate', [])[i],
                            'accessionNumber': recent.get('accessionNumber', [])[i],
                            'primaryDocument': recent.get('primaryDocument', [])[i]
                        }
                        filings.append(filing)
            
            return filings[:5]  # Return last 5 filings
            
        except Exception as e:
            print(f"Error getting recent filings: {e}")
            return []
    
    def get_filing_content(self, cik: str, accession_number: str, primary_document: str) -> Optional[str]:
        """Retrieve the content of a specific filing."""
        try:
            # Construct the filing URL
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number.replace('-', '')}/{primary_document}"
            
            response = self.session.get(filing_url)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Look for specific sections that are most relevant for analysis
            relevant_sections = []
            
            # Try to find specific sections
            section_keywords = [
                'business', 'risk factors', 'management discussion', 'financial statements',
                'consolidated statements', 'balance sheet', 'income statement', 'cash flow',
                'revenue', 'expenses', 'assets', 'liabilities', 'equity'
            ]
            
            # Get all text content
            text_content = soup.get_text()
            
            # Split into paragraphs and find relevant sections
            paragraphs = text_content.split('\n')
            current_section = []
            in_relevant_section = False
            
            for line in paragraphs:
                line = line.strip()
                if not line or len(line) < 10:
                    continue
                
                line_lower = line.lower()
                
                # Check if this line starts a relevant section
                if any(keyword in line_lower for keyword in section_keywords):
                    if current_section and in_relevant_section:
                        relevant_sections.append('\n'.join(current_section))
                    current_section = [line]
                    in_relevant_section = True
                elif in_relevant_section:
                    current_section.append(line)
                    # Limit section length
                    if len(current_section) > 50:
                        relevant_sections.append('\n'.join(current_section))
                        current_section = []
                        in_relevant_section = False
            
            # Add the last section if it exists
            if current_section and in_relevant_section:
                relevant_sections.append('\n'.join(current_section))
            
            # If we found relevant sections, use them
            if relevant_sections:
                content = '\n\n'.join(relevant_sections[:5])  # Use top 5 sections
            else:
                # Fallback to general content extraction
                lines = text_content.split('\n')
                cleaned_lines = []
                
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 20:  # Filter out very short lines
                        cleaned_lines.append(line)
                
                content = '\n'.join(cleaned_lines[:2000])  # Limit to first 2000 lines
            
            return content
            
        except Exception as e:
            print(f"Error getting filing content: {e}")
            return None
    
    def search_and_analyze(self, company_name: str, form_type: str = "10-K") -> Dict:
        """Complete workflow: search company, get filings, and retrieve content."""
        results = {
            'company_name': company_name,
            'companies_found': [],
            'filings': [],
            'content': None,
            'error': None
        }
        
        try:
            # Search for company
            companies = self.search_company(company_name)
            results['companies_found'] = companies
            
            if not companies:
                results['error'] = "No companies found"
                return results
            
            # Use first company found
            company = companies[0]
            cik = company['cik']
            
            # Get recent filings
            filings = self.get_recent_filings(cik, form_type)
            results['filings'] = filings
            
            if not filings:
                results['error'] = f"No {form_type} filings found"
                return results
            
            # Get content of most recent filing
            latest_filing = filings[0]
            content = self.get_filing_content(
                cik, 
                latest_filing['accessionNumber'], 
                latest_filing['primaryDocument']
            )
            
            results['content'] = content
            results['selected_company'] = company
            results['selected_filing'] = latest_filing
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
