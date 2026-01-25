from google import genai
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

        # New SDK Initialization
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-3-flash-preview"

    async def generate_content_async(self, prompt, retries=2):
        """Generates content asynchronously with retry logic using asyncio.to_thread."""
        for attempt in range(retries + 1):
            try:
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=self.model_name,
                    contents=prompt,
                )

                if response and response.text:
                    return response.text
                return None

            except Exception as e:
                msg = str(e)
                if attempt == retries:
                    logger.error(
                        f"LLM generation failed after {retries} retries: {msg}"
                    )
                    return None

                wait_time = 30  # Fixed 30 seconds delay
                logger.warning(
                    f"LLM generation failed (Attempt {attempt + 1}/{retries + 1}): {msg}. Retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)

    def generate_content(self, prompt):
        """Synchronous wrapper."""
        try:
            response = self.client.models.generate_content(
                model=self.model_name, contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return None
