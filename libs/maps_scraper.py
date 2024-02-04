from libs.web_scraping import WebScraping


class MapsScraper(WebScraping):
    
    def __init__(self, postal_code: int, keywords: list, headless: bool = False):
        """ Start chrome and save search text

        Args:
            postal_code (int): Postal code to search
            keywords (list): Keywords to search
            headless (bool, optional): If True, the browser will not be shown.
                Defaults to False.
        """
        
        # Get the url to search
        keywords_str = " ".join(keywords)
        self.search_text = f"{postal_code} {keywords_str}"
        
        # Start scraper
        super().__init__(
            headless=headless,
        )
        
        # Control variables
        self.header_removed = False
        
    def search(self):
        """ Search the url and wait for the results
        """
        
        selectors = {
            "search": 'input[name="q"]',
        }
        self.set_page("https://www.google.com/maps")
        self.refresh_selenium()
        self.send_data(selectors["search"], self.search_text)
        self.send_data(selectors["search"], "\n")
        self.refresh_selenium()
        
    def extract_business(self):
        """ Extract business from the current results page

        Returns:
            list: List of businesses data found
                TODO: Define the data to return
        """
    
        selectors = {
            "header": '[role="feed"] > div:nth-child(1), '
                      '[role="feed"] > div:nth-child(2)',
            "result": '[role="feed"] > div:not(.TFQHme)',
            "separator": '[role="feed"] > div.TFQHme',
        }
        
        # Remove header elements (only first time)
        if not self.header_removed:
            self.remove_elems(selectors["header"])
            self.header_removed = True
        
        # Remove separator elements
        self.remove_elems(selectors["separator"])
        
        # Loop results
        
        # Extract data from each result
        
        # Add css class to each result
        
        
        
    def next_page(self):
        """ Go to the next page of results

        Returns:
            bool: True if there is a next page, False otherwise
        """
        
        pass