import os

import bs4
import requests
from dotenv import load_dotenv

from backend.config import GoogleSearchConfig

load_dotenv()


class SearchService:
    def __init__(self):
        """
        :param api_key: Your Google API key
        :param cx:     Your Custom Search Engine ID
        """
        self.config = GoogleSearchConfig()
        self.api_key = self.config.GOOGLE_API_KEY
        self.cx = self.config.GOOGLE_CX
        if not self.api_key or not self.cx:
            raise ValueError("API_KEY and CX must be set")
        self.url = "https://www.googleapis.com/customsearch/v1"

    def search(self, query: str, num_results: int = 5) -> list[str]:
        params = {
            "key": self.api_key,
            "cx": self.cx,
            "q": query,
            # "num": num_results,
        }
        try:
            resp = requests.get(self.url, params=params)
            resp.raise_for_status()
            data = resp.json()
            if "items" not in data:
                raise ValueError("No items found in the response")

            return self.process_search_results(data["items"])

        except requests.RequestException as e:
            print(f"Error fetching search results: {e}")
            return ()
        except ValueError as e:
            print(f"Error parsing JSON response: {e}")
            return ()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return ()

    def process_search_results(self, results: list[str]) -> list[str]:
        """
        Process the search results to extract relevant information.
        :param results: List of search result snippets
        :return: List of processed snippets
        """
        extracted_text = []
        for result in results:
            url = result.get("link")
            result_response = response = requests.get(url)
            if result_response.status_code == 200:
                soup = bs4.BeautifulSoup(result_response.content, "html.parser")
                text = soup.get_text()
                extracted_text.append((text, url))
        return extracted_text


if __name__ == "__main__":
    # ideally load these from env vars or a secrets store
    API_KEY = os.getenv("GOOGLE_API_KEY")
    CX = os.getenv("GOOGLE_CX")
    if not API_KEY or not CX:
        raise ValueError("API_KEY and CX must be set")
    svc = SearchService(API_KEY, CX)
    print(svc.search("What is the capital of France?"))
