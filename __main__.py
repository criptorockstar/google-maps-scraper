import os
from dotenv import load_dotenv
from libs.maps_scraper import MapsScraper

load_dotenv()
HEADLESS = os.getenv("SHOW_BROWSER") != "True"
POSTAL_CODE = os.getenv("POSTAL_CODE")
KEYWORDS = os.getenv("KEYWORDS").split(",")

if __name__ == "__main__":

    maps_scraper = MapsScraper(POSTAL_CODE, KEYWORDS, HEADLESS)

    # Search postal code and keywords in google maps
    maps_scraper.search()

    # Extract data
    while True:
        data = maps_scraper.extract_business()
        more_pages = maps_scraper.next_page()
        if not more_pages:
            break
