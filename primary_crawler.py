"""crawls google maps for businesses profiles links.

contains the Primary_Stage_Subject_input class which takes the 
Get_Headers_and_URL class as an object, the url and headers of 
a google maps search, crawls their profiles the results pages and 
returns a list of businesses profiles links.

Typical usage example:

    primary_stage = Primary_Stage_Subject_input(Get_Headers_and_URL, search_url, search_headers)
    profiles_list = primary_stage.p_handler(next_page, results_count, search_subject)
"""

from time import time, sleep
from selectolax.parser import HTMLParser
from requests import session as r_session
from tqdm import tqdm
from headers import Get_Headers_and_URL
from typing import List

RESULTS_PER_PAGE = 20
"""int: The number of results per page."""


class Primary_Stage_Master:
    """A class responsible for fetching business profiles from HTML content.

    Methods:
        get_business_profiles(response_text): Extracts profile IDs from the response HTML and stores them in profiles_list.
        fetch_search_pages(session, url): Synchronously fetches the HTML content of a search page from a given URL.
    """
    
    def __init__(self):
        self.profiles_list: List[str] = []

    def get_business_profiles(self, response_text: str) -> None:
        """Extracts business profile IDs from the provided HTML response and appends them to profiles_list.

        Args:
            response_text (str): The HTML content of the search page response.

        Notes:
            Parses HTML to find profile elements and extracts 'jsdata' attributes to obtain unique profile IDs.
        """
        source = HTMLParser(html=response_text)
        
        # Extract profile IDs from 'jsdata' attribute in profile elements
        self.profiles_list += [
            profile.attributes["jsdata"].split(";")[1]
            for profile in source.css('div[jscontroller="XHXkqb"]')
        ]

    def fetch_search_pages(self, session, url: str) -> str:
        """Synchronously fetches the HTML content from the provided URL.

        Args:
            session (requests.Session): The HTTP session used for making requests.
            url (str): The URL of the search page to fetch.

        Returns:
            str: The HTML content of the fetched page.
        """
        response = session.get(url)
        return response.text  # Return HTML content of the search page


class Primary_Stage_Subject_input(Primary_Stage_Master):
    """Handles paginated fetching of business profile data based on subject input.

    Inherits:
        Primary_Stage_Master: Provides profile parsing functionality.

    Attributes:
        profiles_list (List[str]): Accumulated list of profile IDs from all fetched pages.
        search_url (str): Base search URL for fetching profiles.
        search_headers (dict): Headers required for HTTP requests.
        get_headers_and_url_c (Get_Headers_and_URL): Instance for handling dynamic URL and headers fetching.

    Methods:
        p_handler(next_page, results_count, search_subject): Iterates over paginated results, fetching profile data.
    """

    profiles_list: List[str] = []

    def __init__(self, get_headers_and_url: Get_Headers_and_URL, search_url: str, search_headers: dict) -> None:
        """Initializes Primary_Stage_Subject_input with required URL, headers, and handler instance.

        Args:
            get_headers_and_url (Get_Headers_and_URL): Instance for fetching updated headers and URLs.
            search_url (str): Base URL for search queries.
            search_headers (dict): HTTP headers for search requests.
        """
        self.search_url = search_url
        self.search_headers = search_headers
        self.get_headers_and_url_c = get_headers_and_url

    def p_handler(self, next_page: bool, results_count: int, search_subject: str) -> List[str]:
        """Fetches and parses business profiles from paginated search results.

        Args:
            next_page (bool): Whether there is an additional page to load.
            results_count (int): Total number of results available for pagination.
            search_subject (str): The search term for the desired business subject.

        Returns:
            List[str]: List of profile IDs extracted from all fetched pages.
        """
        session = r_session()   
        session.headers = self.search_headers
        
        # Generate list of page offsets based on total result count
        pages_available = list(range(0, results_count, RESULTS_PER_PAGE))
        
        # Adjust the starting page offset if there is already a second page loaded
        if next_page:
            pages_available = pages_available[pages_available.index(2 * RESULTS_PER_PAGE):]

        for page in tqdm(pages_available, unit="page", desc="search page"):
            url = f"{self.search_url}&lci={page}"
            while True:
                try:
                    # Fetch page content and break on successful fetch
                    text_response = self.fetch_search_pages(session, url)
                    break
                except:
                    # Retry fetching URL if there’s an error, reinitialize session and headers if needed
                    session.close()
                    sleep(61)  # Wait before retrying to avoid request limit errors
                    search_url, search_headers, results_count, next_page, _ = self.get_headers_and_url_c().run(search_subject)
                    session = r_session()
                    session.headers = search_headers
            
            # Parse profiles from the response HTML and add to profiles_list
            self.get_business_profiles(text_response)
        
        return self.profiles_list
