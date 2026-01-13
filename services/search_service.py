import requests
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

class SearchService:
    def __init__(self):
        self.api_key = settings.GOOGLE_SEARCH_API_KEY
        self.cx = settings.SEARCH_ENGINE_ID
        
        if not self.api_key or not self.cx:
            logger.warning("Google Search API Key or Search Engine ID is missing.")

    def search_pdf_reports(self, keyword, sites, num_results=10):
        """Search for PDF reports on specific sites."""
        if not self.api_key or not self.cx:
            return []
            
        site_query = " OR ".join([f"site:{site}" for site in sites])
        final_query = f"{keyword} filetype:pdf ({site_query})"
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.api_key,
            'cx': self.cx,
            'q': final_query,
            'num': num_results,
            'dateRestrict': 'w1' # Last week
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get('items', []):
                results.append({
                    'title': item['title'],
                    'link': item['link']
                })
            
            logger.info(f"Found {len(results)} reports for keyword '{keyword}'")
            return results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Google Search failed: {e}")
            return []
