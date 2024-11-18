"""this module is responsible for storing data.

this it contains a calls "Storage" that allows to save
th data of the scraped businesses to a PostgreSQL database.

Typical usage example:

    data_base = Storage() 
    data_base.save_to_sql_(businesses_, location, subject)
"""

import json
import pandas as pd
from datetime import date
from sqlalchemy import create_engine
from dotenv import load_dotenv, dotenv_values

class Storage:
    """Handles data storage and retrieval for business profiles.

    This class provides methods to save results to a PostgreSQL database.

    Attributes:
        today_date (str): The current date formatted as 'MM-DD-YYYY'.
        engine: SQLAlchemy engine for connecting to the database.
    """

    def __init__(self):
        """Initializes the Storage instance and records today's date."""
        self.today_date = date.today().strftime("%m-%d-%Y")

    def get_db_url(self) -> str:
        """Reads database connection parameters from a JSON file and constructs the database URL.

        Returns:
            str: Database connection URL for PostgreSQL.
        """
        db_info = dotenv_values(".env")
        db_url = f"postgresql://{db_info['db_user_name']}:{db_info['db_password']}@localhost:{db_info['db_port']}/{db_info['db_name']}"
        return db_url

    def launch_sql_engine(self) -> None:
        """Initializes the SQLAlchemy engine for database interactions."""
        db_url = self.get_db_url()
        self.engine = create_engine(db_url)

    def end_sql_session(self) -> None:
        """Disposes of the SQLAlchemy engine, ending the database session."""
        self.engine.dispose()

    def save_to_sql_(self, results_list, location: str, subject: str) -> None:
        """Saves the results list to a PostgreSQL database.

        Args:
            results_list (list): List of results to save.
            location (str): The location associated with the business data.
            subject (str): The subject of the search, used for categorization in the database.
        """
        df = pd.DataFrame(results_list)
        df = df.drop_duplicates(subset="profile")  # Remove duplicates based on profile
        df["business_type"] = subject  # Add business type based on the subject
        df["location"] = location  # Add location to the DataFrame
        df["services"] = df["services"].apply(lambda x: str(x).split(", ") if ", " in str(x) else [])  # Convert services to list
        df.to_sql("businesses", self.engine, if_exists="append", index=False)  # Save to SQL table
