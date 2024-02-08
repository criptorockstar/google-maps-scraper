from libs.web_scraping import WebScraping
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        self.set_page("https://www.google.com/maps?hl=en")
        self.refresh_selenium()
        self.send_data(selectors["search"], self.search_text)
        self.send_data(selectors["search"], "\n")
        self.refresh_selenium()

    def extract_business(self) -> dict:
        """ Extract business from the current results page

        Returns:
            dict: Dictionary with the extracted data
            
            Structure:
            {
                "business_name": {
                    "link": str,
                    "website": str,
                    "phone": str
                    "name": str
                }
            }
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
        def loop_results():
            targets = []
            extracted_data = []

            # Retrieve feed data
            results = self.get_elems(selectors["main"])

            print("Negocios encontrados:", len(results))
            time.sleep(10)
            
            # Loop results
            for result in results:
                # Query bussines's names and links
                title_item = result.find_element(
                    By.CSS_SELECTOR,
                    selectors["store.name"]
                ).text
                link_item = result.find_element(
                    By.CSS_SELECTOR,
                    selectors["store.link"]
                ).get_attribute('href')
                
                # Append queried results on temporal list as targets to scrap
                targets.append([title_item, link_item])

            # Loop targets
            print("Recopilando datos..")
            for target in targets:
                # Navigate to target detail's page
                self.set_page(target[1])

                # Wait a resonable amount of seconds to load details's page
                time.sleep(5)

                # Check page's fully loaded
                self.implicit_wait('div.iBPHvd.widget-scene')

                # Extract target's webpage
                website_item = extract_website()

                # Extract target's phone
                phone_item = extract_phone()

                # Append complete target's data
                extracted_data.append([
                    target[0],
                    target[1],
                    website_item,
                    phone_item
                ])

                print(f"extrayendo datos de {target[0]}...")
            
            return extracted_data
        
        def extract_website():
            # Get link elements
            links = self.get_elems('a.CsEnBe')

            # Loop on links
            for link in links:
                # Filter whatsapp links
                if "https://api.whatsapp.com" in link.get_attribute('href'):
                    continue

                # Filter Google bussiness links, any other links are valid
                if "https://business.google.com/" not in link.get_attribute('href'):
                    return link.get_attribute('href')
            
            return None
        
        def extract_phone():
            # Get tab button objects
            objs = self.get_elems('button.CsEnBe')

            # Loop objects
            for obj in objs:
                # Request tab's icons
                obj_icon = obj.find_element(By.CSS_SELECTOR, 'img.Liguzb')
                
                # If object has a phone icon return object's text data
                if "phone_gm_blue_24dp.png" in obj_icon.get_attribute('src'):
                    return obj.text
            
            return None
        
        # Scroll down the page to load all items
        print("Cargando elementos.. Podria tardar unos minutos.")
        self.scroll_page()
        
        # Loop all items in a single loop
        extracted_data = loop_results()

        # Print all items for testing purposes
        return extracted_data

    def implicit_wait(self, selector):
        try:
            WebDriverWait(self.get_browser(), 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
        except Exception:
            self.get_browser().refresh()
            time.sleep(3)

    def scroll_page(self) -> bool:
        """ Go to the next page of results
        Returns:
            bool: True if there is a next page, False otherwise
        """

        # Get feed element
        feed_element = self.get_elem('[role="feed"]')
        
        self.go_bottom()
        self.go_down()

        # Scroll down the whole page to load all results in the D.O.M
        while True:
            # Get current position
            script = "return arguments[0].scrollTop;"
            current_position = self.get_browser().execute_script(script, feed_element)

            # Scroll down
            script = "arguments[0].scrollTop += 1720;"
            self.get_browser().execute_script(script, feed_element)
            
            # Give some time to load new items
            time.sleep(5)
            
            # Get new scroll position
            script = "return arguments[0].scrollTop;"
            new_scroll_position = self.get_browser().execute_script(script, feed_element)

            # If we can't scroll down any more we have reached the bottom
            if new_scroll_position == current_position:
                break