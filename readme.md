# Google Maps Business Data Scraper

## Overview

This project is designed to scrape business data from Google Maps, enabling users to extract and store detailed information about businesses based on specific search queries. The data includes business names, contact information, services, addresses, ratings, and reviews.

## Features

- **Search for Businesses:** Allows users to search for businesses by entering a subject and location.
- **Data Extraction:** Scrapes essential business information from Google Maps.
- **Data Storage:** Supports saving scraped data to a PostgreSQL database.
- **Asynchronous Requests:** Utilizes asynchronous programming to improve performance and handle multiple requests efficiently.

## Technologies Used

- **Python 3.x**: The main programming language used for the scraper.
- **Scrapy**: A powerful web scraping framework for Python, used for extracting data from websites.
- **Playwright**: A library for automating web browsers, used for interacting with Google Maps.
- **Pandas**: A data manipulation library for saving data to a PostgreSQL database and handling data frames.
- **SQLAlchemy**: An SQL toolkit and Object-Relational Mapping (ORM) library for Python, used for database interactions.
- **UserAgent**: A library for generating random user-agent strings to mimic different browsers.

## Installation

### Prerequisites

- Python 3.x
- PostgreSQL Database

### Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/google-maps-scraper.git
cd google-maps-scraper
```

## File Structure

```bash
"google maps ai plece subject input"
│
├── business_profile_DC.py          # Data class of the scraped data
├── calculate_time.py               # Calculate the scraping time
├── secondary_crawler.py            # Scrapes each business profile data
├── headers.py                      # Extract tokens to be used in the crawling
├── main.py                         # Entry point for running the scraper
├── primary_crawler.py              # Crawls the businesses profiles links
├── requirements.txt                # Python package dependencies
├── google maps db settings.json    # Database connection settings
├── storage_solution.py             # Saves the scraped data
└── outputs/                        # Directory for saving scraped CSV files
```
> Please note that this project is posted mainly for demonstration purposes and the script does not work anymore as Google has updated their APIs multiple times. 
