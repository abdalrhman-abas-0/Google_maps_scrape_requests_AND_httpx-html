from time import time, sleep
import asyncio
from pprint import pprint

from headers import Get_Headers_and_URL
from primary_crawler import Primary_Stage_Subject_input
from secondary_crawler import Secondary_Stage
from storage_solution import Storage
from calculate_time import Calculate_Runtime
    
    
def search_subject_and_location_input(subject: str, location: str) -> None:
    """Searches for businesses based on the given subject and location, stores results in a database and CSV file.

    This function orchestrates the process of retrieving business profiles from a web source, processing them, 
    and saving the results to both a PostgreSQL database and a CSV file.

    Args:
        subject (str): The subject of the search (e.g., "Plumber").
        location (str): The location for the search (e.g., "New York").

    Raises:
        Exception: Raises an exception if any error occurs during the data fetching process.
    """
    # Initialize the storage class for database interactions
    data_base = Storage()
    data_base.launch_sql_engine()  # Launch the SQL engine

    # Format the search subject with location
    search_subject = f"{subject} in {location}, USA"
    print(f"searching for {search_subject}.\n")
    
    start_time = time()  # Record the start time for runtime calculation
    
    # Fetch search URL, headers, results count, and page contents
    search_url, search_headers, results_count, next_page, pages_contents_list = Get_Headers_and_URL().run(search_subject)
    
    # Initialize the primary stage class for extracting business profiles
    primary_stage = Primary_Stage_Subject_input(Get_Headers_and_URL, search_url, search_headers)

    # Process each page's content to get business profiles
    for page_content in pages_contents_list:
        primary_stage.get_business_profiles(page_content)

    # Handle pagination and get all profiles
    profiles_list = primary_stage.p_handler(next_page, results_count, search_subject)
    
    # Initialize the secondary stage class to fetch detailed business data asynchronously
    secondary_stage_class = Secondary_Stage()
    businesses_ = asyncio.run(secondary_stage_class.s_handler(profiles_list))
    
    # Save the fetched business data to SQL
    data_base.save_to_sql_(businesses_, location, subject)

    # Calculate and print runtime
    hours, minutes, seconds = Calculate_Runtime(start_time)
    print(f"scraped {len(businesses_)} results successfully in {hours}:{minutes}:{seconds}.")

    print("\n")
    data_base.end_sql_session()  # Close the SQL session
    print(f"\ndone {'-'*50}")

       
if __name__ == "__main__":
    subject = "dentist"
    locations = "Austin, TX"
    search_subject_and_location_input(subject, locations)

