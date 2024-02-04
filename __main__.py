import os
from dotenv import load_dotenv
from libs.maps_scraper import MapsScraper

load_dotenv()
HEADLESS = os.getenv("SHOW_BROWSER") != "True"
POSTAL_CODE = os.getenv("POSTAL_CODE")
KEYWORDS = os.getenv("KEYWORDS").split(",")
    
if __name__ == "__main__":
    maps_scraper = MapsScraper(POSTAL_CODE, KEYWORDS, HEADLESS)
    maps_scraper.search()
    while True:
        maps_scraper.extract_business()
        more_pages = maps_scraper.extract_business()
        if not more_pages:
            break