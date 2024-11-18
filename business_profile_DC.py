"""responsible for cleaning and validation of the businesses data.

Typical usage example:

    from dataclasses import asdict
    
    business_data = BusinessProfile(
        profile="profile_link_on_google",
        business="business name",
        website="business website",
        phone_number="phon number",
        services="services offered",
        address="address",
        rating="rating",
        reviews="reviews count"
    )
    business_data_dict = asdict(business_data)
"""

from dataclasses import dataclass, asdict
from typing import Optional
import re

@dataclass
class BusinessProfile:
    """Represents a business profile with contact and review information.

    Attributes:
        profile (str): The name or profile of the business owner or main entity.
        business (str): The name of the business.
        website (Optional[str]): The website URL of the business, if available.
        phone_number (Optional[str]): The contact phone number of the business, if available.
        services (Optional[str]): A description of services provided by the business, if available.
        address (Optional[str]): The address of the business, if available.
        rating (Optional[str]): The rating of the business, if available, initially a string (converted to float).
        reviews (Optional[str]): The number of reviews, if available, initially a string (converted to int).
    """

    profile: str
    business: str
    website: Optional[str] = None
    phone_number: Optional[str] = None
    services: Optional[str] = None
    address: Optional[str] = None
    rating: Optional[str] = None
    reviews: Optional[str] = None

    def __post_init__(self):
        """Cleans and converts data for `services`, `reviews`, and `rating` after initialization."""
        self.clean_service()
        self.clean_reviews()
        self.clean_rating()
        
    def clean_service(self):
        """Removes the 'Services: ' prefix from `services` if it exists."""
        if self.services:
            # Removes the 'Services: ' prefix if present
            self.services = self.services.strip("Services: ")
    
    def clean_reviews(self):
        """Extracts a numeric value from `reviews` and converts it to an integer.

        If `reviews` contains no numeric value, sets `reviews` to None.
        """
        if self.reviews:
            # Extracts the first numeric sequence in `reviews` and converts it to int
            match = re.search(r"\d+", self.reviews)
            self.reviews = int(match[0]) if match else None

    def clean_rating(self):
        """Converts the `rating` attribute to a float if it can be parsed.

        If `rating` cannot be converted to a float, sets `rating` to None.
        """
        if self.rating:
            try:
                self.rating = float(self.rating)
            except ValueError:
                self.rating = None

