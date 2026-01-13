import io
import aiohttp
import asyncio
from pypdf import PdfReader
from utils.logger import setup_logger

logger = setup_logger(__name__)

class CrawlerService:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0'}

    async def extract_text_from_url(self, url, timeout=15):
        """Downloads PDF from URL and extracts text asynchronously."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, timeout=timeout) as response:
                    if response.status != 200:
                        logger.warning(f"Failed to download {url}: Status {response.status}")
                        return None
                    
                    content = await response.read()
                    
                    # Run CPU-bound extraction in a separate thread
                    text = await asyncio.to_thread(self._extract_text_from_bytes, content)
                    
                    if text and len(text) > 500:
                        return text
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"Timeout downloading {url}")
            return None
        except Exception as e:
            logger.error(f"Error extracting text from {url}: {e}")
            return None

    def _extract_text_from_bytes(self, content):
        """Extracts text from PDF bytes (CPU bound)."""
        try:
            f = io.BytesIO(content)
            reader = PdfReader(f)
            text = ""
            # Limit to first 10 pages to avoid processing huge files
            for i in range(min(len(reader.pages), 10)):
                page_text = reader.pages[i].extract_text()
                if page_text:
                    text += page_text
            return text
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return None
