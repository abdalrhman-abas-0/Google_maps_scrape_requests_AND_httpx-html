"""asynchronously crawls businesses profiles on google maps.

contains the Secondary_Stage class which takes businesses profiles links
on google maps and returns and asynchronously crawls their profiles, 
parse the html and reuters the response as a list.

Typical usage example:

    secondary_stage_class = Secondary_Stage()
    businesses_ = asyncio.run(secondary_stage_class.s_handler(profiles_list))
"""

from time import time, sleep
from selectolax.parser import HTMLParser
from tqdm import tqdm
from fake_useragent import UserAgent
from httpx_html import AsyncHTMLSession
import asyncio

from business_profile_DC import BusinessProfile
from dataclasses import asdict
from typing import List, Tuple

SECONDARY_STAGE_HEADERS = {
    "User-Agent": "",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Alt-Used": "www.google.com",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site"
} 
"""dict: Headers to be used in secondary stage requests."""

CALL_RATE = 120
"""int: Maximum number of profiles to process in a single batch."""


class Secondary_Stage:
    """Handles asynchronous fetching and processing of business data from given profile URLs.

    Attributes:
        business_info_list (list): Stores extracted business information as dictionaries.
        ua (UserAgent): Randomized user agent generator for request headers.
    """
    
    business_info_list = []
    ua = UserAgent()

    async def fetch_businesses(self, session: AsyncHTMLSession, url: str) -> Tuple[str, str]:
        """Fetches business HTML data from the provided URL asynchronously.

        Args:
            session (AsyncHTMLSession): The session for making HTTP requests.
            url (str): The target URL to fetch.

        Returns:
            Tuple[str, str]: A tuple containing the HTML content and the URL.

        Raises:
            Exception: If the response status is not 200 (OK).
        """
        response = await session.get(url)
        if response.status_code != 200:
            raise Exception("Connection error!")
        return response.text, url

    def create_profiles_array(self, profiles_list: List[str]) -> List[List[str]]:
        """Divides a list of profiles into smaller arrays based on the CALL_RATE limit.

        Args:
            profiles_list (list): List of profile URLs.

        Returns:
            list: Nested list of profile URLs, split according to CALL_RATE.
        """
        if CALL_RATE >= len(profiles_list):
            profiles_arrays = [profiles_list]
        else:
            profiles_arrays = []
            sub_list = []

            # Split profiles_list into sub-lists based on CALL_RATE
            for profile in profiles_list:
                sub_list.append(profile)
                if (profiles_list.index(profile) + 1) % CALL_RATE == 0 or profile is profiles_list[-1]:
                    profiles_arrays.append(sub_list)
                    sub_list = []
        return profiles_arrays

    def get_business_data(self, responses_list: List[Tuple[str, str]]) -> None:
        """Parses and extracts business data from HTML responses.

        Args:
            responses_list (list): List of tuples containing HTML content and profile URL.
        """
        for source_code, profile in responses_list:
            source = HTMLParser(html=source_code)
            
            # Append parsed business data as a dictionary to business_info_list
            self.business_info_list.append(
                asdict(
                    BusinessProfile(
                        profile=profile,
                        business=source.css_first("div.rgnuSb.tZPcob").text(),
                        website=source.css_first("div.Gx8NHe").text(),
                        phone_number=source.css_first("div.eigqqc").text(),
                        services=source.css_first("div.AQrsxc").text(),
                        address=source.css_first("div.hgRN0").text(),
                        rating=source.css_first("span.ZjTWef.QoUabe").text(),
                        reviews=source.css_first("span.PN9vWe").text()
                    )
                )
            )

    async def s_handler(self, profiles_list: List[str]) -> List[dict]:
        """Manages the asynchronous session for fetching business data and handles session errors and retry logic.

        Args:
            profiles_list (list): List of profile URLs to fetch data from.

        Returns:
            list: List of business information dictionaries.
        """
        async_session = AsyncHTMLSession()
        headers_ = SECONDARY_STAGE_HEADERS
        headers_["User-Agent"] = self.ua.random
        async_session.headers = headers_

        # Split profiles list into arrays based on CALL_RATE
        profiles_arrays = self.create_profiles_array(profiles_list)

        for profiles_sub_list in tqdm(profiles_arrays, unit="list", desc="business array"):
            while True:
                try:
                    start = time()
                    
                    # Create async tasks for each profile in the sub-list
                    co_routines = [asyncio.create_task(self.fetch_businesses(async_session, profile)) for profile in profiles_sub_list]
                    responses_list = await asyncio.gather(*co_routines)
                    break  # Exit loop if requests are successful
                except:
                    # Close session on failure and retry after delay
                    await async_session.close()
                    print("\nSession error, retrying...")
                    # Wait to respect rate limit if needed
                    try:
                        sleep(61 - (time() - start))
                    except:
                        pass
                    
                    # Reinitialize session with randomized User-Agent
                    async_session = AsyncHTMLSession()
                    headers_ = SECONDARY_STAGE_HEADERS
                    headers_["User-Agent"] = self.ua.random
                    async_session.headers = headers_

            # Process the responses and extract business data
            self.get_business_data(responses_list)

            # Wait before the next set of requests if not the last batch
            if profiles_sub_list is not profiles_arrays[-1]:
                try:
                    sleep(61 - (time() - start))
                except:
                    pass

        # Return the full list of extracted business information
        return self.business_info_list
