import google.generativeai as genai
import asyncio
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

class LLMService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            logger.error("Gemini API Key is missing.")
            raise ValueError("Gemini API Key is missing.")
            
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    async def generate_content_async(self, prompt, retries=3):
        """Generates content asynchronously with simple retry logic."""
        for attempt in range(retries):
            try:
                # Use generate_content_async if available (recent SDKs)
                # If not, wrap synchronous call
                if hasattr(self.model, 'generate_content_async'):
                    response = await self.model.generate_content_async(prompt)
                else:
                    response = await asyncio.to_thread(self.model.generate_content, prompt)
                
                return response.text
            except Exception as e:
                logger.warning(f"LLM generation failed (Attempt {attempt+1}/{retries}): {e}")
                if attempt == retries - 1:
                    return f"Error: {e}"
                await asyncio.sleep(2 ** attempt) # Exponential backoff

    def generate_content(self, prompt):
        """Synchronous wrapper for compatibility if needed."""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return f"Error: {e}"
