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
        """Search for PDF reports on specific sites (handles >10 results via pagination)."""
        if not self.api_key or not self.cx:
            return []

        site_query = " OR ".join([f"site:{site}" for site in sites])
        final_query = f"{keyword} filetype:pdf ({site_query})"
        url = "https://www.googleapis.com/customsearch/v1"

        all_results = []
        fetched_count = 0

        # Google Search allows max 10 results per call
        # We loop until we reach num_results
        while fetched_count < num_results:
            # How many to fetch in this batch (max 10)
            batch_size = min(num_results - fetched_count, 10)
            start_index = fetched_count + 1  # 1-based index

            params = {
                "key": self.api_key,
                "cx": self.cx,
                "q": final_query,
                "num": batch_size,
                "start": start_index,
                "dateRestrict": "w1",
            }

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                items = data.get("items", [])
                if not items:
                    break  # No more results found

                for item in items:
                    all_results.append({"title": item["title"], "link": item["link"]})

                fetched_count += len(items)

                # If we got fewer items than requested, we reached the end
                if len(items) < batch_size:
                    break

            except requests.exceptions.RequestException as e:
                logger.error(f"Google Search failed at start={start_index}: {e}")
                break

        logger.info(
            f"Found {len(all_results)} reports for keyword '{keyword}' (Requested: {num_results})"
        )
        return all_results
