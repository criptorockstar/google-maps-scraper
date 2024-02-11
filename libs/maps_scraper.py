from libs.web_scraping import WebScraping
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

    def __loop_results__(self, selectors):
        targets = []

        # Retrieve feed data
        results = self.get_elems(selectors["main"])

        print("Negocios encontrados:", len(results))

        for result in results:
            title = self.get_text(result, selectors["name"])
            link = self.get_attrib('href', result, selectors["link"])

            # Append queried results on temporal list as targets to scrap
            targets.append([title, link])

        return targets

    def __get_data__(self, selectors, targets):
        extracted_data = []

        print("Recopilando datos..")
        for target in targets:
            self.set_page(target[1])

            # Wait a resonable amount of seconds to load details's page
            time.sleep(10)

            # Check page's fully loaded
            self.implicit_wait(selectors["element"])

            # Get phone
            phone = self.get_text(selectors["phone"])

            # Get website
            website = self.get_text(selectors["website"])

            print(f"extrayendo datos de {target[0]}...")

            extracted_data.append([
                target[0],
                self.clear(website),
                self.clear(phone)
            ])

        return extracted_data

    def search(self):
        """ Search the url and wait for the results
        """

        selectors = {
            "search": 'input[name="q"]',
        }
        self.set_page("https://www.google.com/maps?hl=en")  # Forced to english
        self.refresh_selenium()
        self.send_data(selectors["search"], self.search_text)
        self.send_data(selectors["search"], "\n")
        self.refresh_selenium()

    def extract_business(self):
        """ Extract business from the current results page

        Returns:
            list: List of businesses data found

            [[name,
              website,
              phone
            ]]
        """

        selectors = {
            "header": '[role="feed"] > div:nth-child(1), '
                      '[role="feed"] > div:nth-child(2)',
            "result": '[role="feed"] > div:not(.TFQHme)',
            "separator": '[role="feed"] > div.TFQHme',
            "main": 'div.Nv2PK.THOPZb.CpccDe',
            "link": 'a.hfpxzc',
            "name": 'div.qBF1Pd',
            "phone": '[data-item-id^="phone"] .fontBodyMedium',
            "website": '[data-item-id^="authority"] .fontBodyMedium',
            "element": 'div.iBPHvd.widget-scene',
            "feed": '[role="feed"]'
        }

        # Remove header elements (only first time)
        if not self.header_removed:
            self.remove_elems(selectors["header"])
            self.header_removed = True

        # Remove separator elements
        self.remove_elems(selectors["separator"])

        # Scroll down the page to load all items
        print("Cargando elementos.. Podria tardar unos minutos.")
        self.infinite_scroll(selectors["feed"])

        # Loop results
        targets = self.__loop_results__(selectors)

        # Get data
        extracted_data = self.__get_data__(selectors, targets)

        return extracted_data
