from libs.web_scraping import WebScraping
from selenium.webdriver.common.by import By
import time


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

        # Store data
        self.extracted_data = {}

        # Store zip_code
        self.zipcode = postal_code


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
            "main": 'div.Nv2PK.THOPZb.CpccDe',
            "store.link": 'a.hfpxzc',
            "store.name": 'div.qBF1Pd',
            "store.items": 'div.AeaXub div.rogA2c div.Io6YTe.fontBodyMedium.kR99db'
        }

        # Remove header elements (only first time)
        if not self.header_removed:
            self.remove_elems(selectors["header"])
            self.header_removed = True

        # Remove separator elements
        self.remove_elems(selectors["separator"])

        # Loop results
        for index in range(0, len(self.get_elems(selectors["main"]))):
            results = self.get_elems(selectors["main"])
            result = results[index]
            
            extracted_data = self.extract_data(selectors, result)

            unique_id = extracted_data["name"]

            self.extracted_data[unique_id] = extracted_data

        datos = self.extracted_data

        for clave, valor in datos.items():
            print("Nombre:", valor['name'])
            print("Sitio web:", valor['website'])
            print("Teléfono:", valor['phone'])
            print()

        # Extract data from each result
    def extract_data(self, selectors, result):
        link_item = result.find_element(By.CSS_SELECTOR, selectors["store.link"]).get_attribute('href')
        title_item = result.find_element(By.CSS_SELECTOR, selectors["store.name"]).text

        self.set_page(link_item)
        self.refresh_selenium()

        website_item = None
        try:
            self.wait_load('a.CsEnBe')
            links, website_item = self.get_elems('a.CsEnBe'), None
            for link in links:
                if "https://api.whatsapp.com" in link.get_attribute('href'):
                    pass

                website = link.get_attribute('href')
                if "https://business.google.com/" in website:
                    website_item = None
                else:
                    website_item = website
        except:
            pass

        phone_item = None
        try:
            objs = self.get_elems('button.CsEnBe')
            for obj in objs:
                phone = obj.find_element(By.CSS_SELECTOR, 'img.Liguzb')
                
                if "phone_gm_blue_24dp.png" in phone.get_attribute('src'):
                    phone_item = obj.text
        except:
            pass
                
        # Add class to avoid store duplicated results
        #self.add_class(result)
                
        # Go Back
        self.get_browser().back()
        self.refresh_selenium()

        return {
            "name": title_item,
            "website": website_item,
            "phone": phone_item
        }


        # Add css class to each result
    def add_class(self, elem):
        self.get_browser().execute_script(
        f"arguments[0].setAttribute('class', 'stored');", elem)


    def next_page(self) -> bool:
        """ Go to the next page of results
        Returns:
            bool: True if there is a next page, False otherwise
        """

        pass
