import os
from dotenv import load_dotenv
from libs.maps_scraper import MapsScraper
from libs.google_sheets import SheetsManager

# Paths
CURRENT_FOLDER = os.path.dirname(__file__)
CRED_PATH = os.path.join(CURRENT_FOLDER, "google_sheets.json")

# Env variables
load_dotenv()
HEADLESS = os.getenv("SHOW_BROWSER") != "True"
POSTAL_CODE = os.getenv("POSTAL_CODE")
KEYWORDS = os.getenv("KEYWORDS").split(",")
GOOGLE_SHEET = os.getenv("GOOGLE_SHEET")

if __name__ == "__main__":

    maps_scraper = MapsScraper(POSTAL_CODE, KEYWORDS, HEADLESS)

    # Search postal code and keywords in google maps
    maps_scraper.search()

    # Extract data
    data = maps_scraper.extract_business()
    
    for row in data:
        row.append(POSTAL_CODE)
    
    # Save data in google sheetsç
    sheets_manager = SheetsManager(GOOGLE_SHEET, CRED_PATH, "data")
    sheets_manager.write_data(data, 2)