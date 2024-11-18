"""gets the data necessary for crawling like headers, urls, and more...

through the Get_Headers_and_URL class it returns search url, search headers, results count,
if there are more than one page for the search, and a list of pages contents list as the bot
may not be able to catch the headers on the first page thus must try to extract them
from the next page.

Typical usage example:
    
    search_url, search_headers, results_count, next_page, pages_contents_list = Get_Headers_and_URL().run(search_subject)
"""

from playwright.sync_api import Playwright, sync_playwright, expect
from time import time, sleep
import re

from typing import List, Tuple

class Headers_Master:
    """Handles header management, language settings, and search URL extraction for Google Local Services.

    Attributes:
        API (str): The base URL for the API endpoint.
        search_url (str): Stores the modified search URL after intercepting requests.
        search_headers (dict): Contains headers from intercepted requests.
        profiles_list (list): Holds a list of profiles retrieved from the API.
        next_page (bool): Indicates whether there is a next page in the search results.
    """
    
    API = "https://www.google.com/localservices/prolist"
    search_url = ""
    search_headers = {}
    profiles_list = []
    next_page = False

    def __route_intercept__(self, route):
        """Intercepts and processes route requests matching the API URL.

        Removes certain query parameters and specific headers, such as 'cookie',
        from the request.

        Args:
            route: The intercepted route object from which headers and URL are extracted.

        Returns:
            route: The original route after modification.
        """
        # Check if the request URL matches the target API URL
        if self.API in route.request.url:
            # Remove specific query parameter from the URL
            self.search_url = re.sub(r"\&lci\=\d+", "", route.request.url)
            # Store the request headers in `search_headers`
            self.search_headers = route.request.all_headers()
            try:
                # Attempt to remove 'cookie' from headers if it exists
                del self.search_headers["cookie"]
            except KeyError:
                pass  # Do nothing if 'cookie' header is not present

        return route.continue_()

    def change_language(self, page):
        """Changes the page language to English, if applicable.

        Attempts to locate a link with a specific role and name, and clicks on it
        to change the page language.

        Args:
            page: The page object on which the language change action is performed.

        Returns:
            The page object after attempting the language change.
        """
        try:
            # Look for a link with role "link" and name "English" and click it
            page.get_by_role("link", name="English").click()
        except:
            pass  # Ignore exceptions if the language link is not found

        return page

    def get_results_count(self, results_available):
        """Extracts and sets the count of available results from a string.

        Parses the `results_available` string to extract the last integer, which
        represents the count of available results.

        Args:
            results_available (str): A string containing the count of available results.

        Sets:
            results_count (int): The parsed integer value of available results.
        """
        # Extract the last integer found in the `results_available` string
        self.results_count = int(re.findall(r"(?<=\s)\d+", results_available)[-1])


class Get_Headers_and_URL(Headers_Master):
    """Handles browser automation to retrieve headers, search URL, and page contents from Google Local Services.

    Inherits:
        Headers_Master: The parent class that manages headers and route interception.
    """
    
    def run(self, search_subject_location) -> tuple:
        """Executes a search on Google, capturing headers, URL, and page contents for local service profiles.

        Automates a search using Playwright, intercepts network requests, and retrieves headers, search URL, and page content.
        
        Args:
            search_subject_location (str): The location-based search query to be entered on Google.

        Returns:
            tuple: Contains the intercepted search URL, request headers, total results count, pagination status,
                   and a list of page contents from the search.
        """
        
        # List to store HTML contents of each page loaded in the browser session
        pages_contents_list = []
        
        # Initialize a Playwright instance and launch a Chromium browser
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False, slow_mo=500)
            context = browser.new_context()  # Create a new browser context
            page = context.new_page()  # Open a new page within the context
            
            # Set up route interception to modify headers and URL as requests are made
            page.route("**/*", self.__route_intercept__)
            
            # Navigate to the Google homepage and wait for the page to load
            page.goto("https://www.google.com")
            page.wait_for_load_state(state="networkidle")
            
            # Change language to English, if possible
            page = self.change_language(page)
            
            # Enter the search query in the Google search bar
            page.get_by_label("Search", exact=True).click()
            page.get_by_label("Search", exact=True).fill(search_subject_location)
            sleep(0.5)  # Brief pause to ensure the page registers the input
            
            try:
                # Trigger the search by simulating the Enter key press
                page.keyboard.press("Enter")
            except:
                pass  # Ignore exceptions if search is already triggered

            page.wait_for_load_state(state="networkidle")
            
            # Click on the link to Google Local Services, if present
            page.wait_for_selector('g-more-link > a[href*="https://www.google.com/localservices/prolist?"]').click()
            page.wait_for_load_state(state="networkidle")
            
            # Append the HTML content of the current page to the list
            pages_contents_list.append(page.content())
            
            try:
                # Attempt to navigate to the next page of results, if available
                page.locator('button[aria-label="Next"]').click()
                page.wait_for_load_state(state="networkidle")
                
                # Extract and store the total results count
                self.get_results_count(page.wait_for_selector('div.AIYI7d[aria-label*="Showing results"]').inner_html())
                
                # Append the HTML content of the next page to the list
                pages_contents_list.append(page.content())
                
                # Indicate that pagination is available
                self.next_page = True
            except:
                # Log message if no further pages are available
                print("No more pages available!")
            
            # Close the browser context and browser instance
            context.close()
            browser.close()
        
        # Return the search URL, headers, results count, pagination status, and all captured page contents
        return self.search_url, self.search_headers, self.results_count, self.next_page, pages_contents_list


class Get_Headers_Subject(Headers_Master):
    """Handles the extraction of search subject and location, along with retrieving headers and page contents from a specified Google search URL.
    
    Inherits:
        Headers_Master: The parent class that manages headers and route interception.
    """

    def extract_subject_and_location(self, raw_search_input: str) -> None:
        """Extracts the search subject and location from a raw search input string.

        Splits the input string by ' in ' to separate subject and location.

        Args:
            raw_search_input (str): The raw search input string containing both subject and location.
        """
        
        # Split the input string by " in " to separate subject and location
        search_input = raw_search_input.split(" in ")
        self.search_subject = search_input[0]
        self.search_location = search_input[1]

    def run(self, search_page_url: str) -> Tuple[str, str, dict, int, bool, list]:
        """Executes navigation to a specified Google search page URL, capturing headers, subject, location, and page content.

        Automates a search using Playwright, extracts the subject and location from the search bar,
        and intercepts headers and page content for local service profiles.
        
        Args:
            search_page_url (str): The URL to navigate for the search results page.

        Returns:
            Tuple: Contains the search subject, search location, request headers, total results count, pagination status,
                   and a list of page contents from the search.
        """
        
        # List to store HTML contents of each page loaded in the browser session
        pages_contents_list = []
        
        # Initialize Playwright instance and launch a Chromium browser
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False, slow_mo=500)
            context = browser.new_context()  # Create a new browser context
            page = context.new_page()  # Open a new page within the context
            
            # Set up route interception to modify headers and URL as requests are made
            page.route("**/*", self.__route_intercept__)
            
            # Navigate to Google homepage and wait for the page to load
            page.goto("https://www.google.com")
            page.wait_for_load_state(state="networkidle")
            
            # Change language to English, if possible
            page = self.change_language(page)
            page.wait_for_load_state(state="networkidle")
            
            # Go to the specified search page URL
            page.goto(search_page_url)
            page.wait_for_load_state(state="networkidle")
            
            # Extract the search subject and location from the search input field
            raw_search_input = page.wait_for_selector('input[aria-label="Search for a service"]').get_attribute("value")
            self.extract_subject_and_location(raw_search_input)
            
            # Append the HTML content of the current page to the list
            pages_contents_list.append(page.content())
            
            try:
                # Attempt to navigate to the next page of results, if available
                page.locator('button[aria-label="Next"]').click()
                page.wait_for_load_state(state="networkidle")
                
                # Extract and store the total results count
                self.get_results_count(page.wait_for_selector('div.AIYI7d[aria-label*="Showing results"]').inner_html())
                
                # Append the HTML content of the next page to the list
                pages_contents_list.append(page.content())
                
                # Indicate that pagination is available
                self.next_page = True
            except:
                # No more pages or 'Next' button not found; continue without error
                pass
            
            # Close the browser context and browser instance
            context.close()
            browser.close()
        
        # Return the search subject, location, headers, results count, pagination status, and all captured page contents
        return self.search_subject, self.search_location, self.search_headers, self.results_count, self.next_page, pages_contents_list
