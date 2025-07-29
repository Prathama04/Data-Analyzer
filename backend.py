# backend.py

import pandas as pd
import io
import time # To simulate loading time for AI functions
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import warnings

# For SharePoint - you'll need to install this: pip install Office365-REST-Python-Client
try:
    from office365.runtime.auth.client_credential import ClientCredential
    from office365.sharepoint.client_context import ClientContext
    sharepoint_client_available = True
except ImportError:
    warnings.warn("Office365-REST-Python-Client not found. SharePoint functionality will be simulated.")
    sharepoint_client_available = False

# Import the new Summarizer class from summarizer.py
from summarizer import Summarizer 



def load_excel_csv(file_path):
    """
    Loads data from an Excel (.xlsx) or CSV (.csv) file into a pandas DataFrame.
    """
    if not file_path:
        raise ValueError("No file path provided.")
    print(f"Loading file: {file_path}")
    time.sleep(1) # Simulate file loading time
    try:
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.lower().endswith('.xlsx') or file_path.lower().endswith('.xls'):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file type. Please upload a .csv, .xlsx, or .xls file.")
        print(f"Successfully loaded {df.shape[0]} rows from {file_path}.")
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except pd.errors.EmptyDataError:
        raise ValueError("The file is empty or has no data.")
    except Exception as e:
        raise Exception(f"Error loading file: {e}")

def load_sql_table(dialect, username, password, host, port, database, sql_query):
    """
    Connects to a SQL database and loads data using the provided SQL query.
    Uses SQLAlchemy for database connection.
    """
    if dialect.lower() == 'sqlite':
        database_url = f"{dialect}:///{database}"
    else:
        database_url = f"{dialect}://{username}:{password}@{host}:{port}/{database}"

    print(f"Attempting to connect to SQL database: {dialect} on {host}:{port}/{database}")
    print(f"Executing query: {sql_query}")
    time.sleep(2) # Simulate connection and query latency

    try:
        engine = create_engine(database_url)
        with engine.connect() as connection:
            df = pd.read_sql(sql_query, connection)

        if df.empty:
            print("SQL query returned an empty DataFrame.")
            raise ValueError("No data returned for the given SQL query. Check query or database content.")

        print(f"Successfully loaded {df.shape[0]} rows from SQL database.")
        return df

    except SQLAlchemyError as e:
        raise ConnectionError(f"Failed to load SQL data. Check connection details (dialect, username, password, host, port, database) and SQL query syntax. Error: {e}")
    except Exception as e:
        raise ConnectionError(f"An unexpected error occurred during SQL data loading: {e}")

def load_sharepoint_list(site_url, list_name, client_id, client_secret):
    """
    Connects to a SharePoint list and loads its data into a pandas DataFrame.
    Requires Office366-REST-Python-Client and proper Azure AD App registration.
    """
    print(f"Attempting to connect to SharePoint list: '{list_name}' at '{site_url}'")
    time.sleep(3) # Simulate connection and loading latency

    if not sharepoint_client_available:
        warnings.warn("Office365-REST-Python-Client not installed. Simulating SharePoint data load.")
        return _simulate_sharepoint_data(list_name)

    try:
        credentials = ClientCredential(client_id, client_secret)
        ctx = ClientContext(site_url).with_credentials(credentials)
        sp_list = ctx.web.lists.get_by_title(list_name)
        list_items = sp_list.get_items().execute_query()
        data = [item.properties for item in list_items]

        if not data:
            print(f"SharePoint list '{list_name}' returned no data.")
            raise ValueError("SharePoint list returned no data. Check list name or permissions.")

        df = pd.DataFrame(data)
        print(f"Successfully loaded {df.shape[0]} rows from SharePoint list '{list_name}'.")
        return df

    except Exception as e:
        print(f"Failed to load real SharePoint data. Error: {e}")
        raise ConnectionError(f"Failed to load SharePoint List. Check site URL, list name, Client ID, Client Secret, and Azure AD app permissions. Error: {e}")

def _simulate_sharepoint_data(list_name):
    """
    Helper function to generate dummy SharePoint data if real connection fails or client not installed.
    """
    print(f"Generating simulated SharePoint data for list '{list_name}'.")
    dummy_data = {
        'ID': [101, 102, 103, 104, 105],
        'Title': [f'{list_name} Item A', f'{list_name} Item B', f'{list_name} Item C', f'{list_name} Item D', f'{list_name} Item E'],
        'CreatedBy': ['John Doe', 'Jane Smith', 'John Doe', 'Peter Jones', 'Jane Smith'],
        'Status': ['Active', 'Pending', 'Active', 'Closed', 'Pending'],
        'Value': [150.75, 200.00, 75.20, 300.50, 120.00],
        'CreatedDate': pd.to_datetime(['2024-01-15', '2024-02-20', '2024-03-10', '2024-04-01', '2024-05-05'])
    }
    df = pd.DataFrame(dummy_data)
    return df

# --- NEW DataAnalyzer Class ---
class DataAnalyzer:
    def __init__(self):
        self.df = None
        self.summarizer = None

    def load_data(self, data_source: str, **kwargs):
        """
        Generic method to load data based on the source.
        Dispatches to the appropriate loading function.
        """
        try:
            if data_source == "file":
                self.df = load_excel_csv(kwargs.get('file_path'))
            elif data_source == "sql":
                self.df = load_sql_table(
                    kwargs.get('dialect'),
                    kwargs.get('username'),
                    kwargs.get('password'),
                    kwargs.get('host'),
                    kwargs.get('port'),
                    kwargs.get('database'),
                    kwargs.get('sql_query')
                )
            elif data_source == "sharepoint":
                self.df = load_sharepoint_list(
                    kwargs.get('site_url'),
                    kwargs.get('list_name'),
                    kwargs.get('client_id'),
                    kwargs.get('client_secret')
                )
            else:
                raise ValueError(f"Unsupported data source: {data_source}")

            # Once data is loaded and initially cleaned, initialize the Summarizer
            if self.df is not None:
                self.summarizer = Summarizer(self.df)
            else:
                self.summarizer = None
            
            return self.df # Return the loaded DataFrame for preview in GUI

        except Exception as e:
            self.df = None # Ensure df is reset on error
            self.summarizer = None
            raise e # Re-raise the exception to be caught by the GUI layer

    def get_data_summary(self) -> tuple[str, list]:
        """
        Delegates the summarization and plotting task to the Summarizer instance.
        """
        if self.summarizer and self.df is not None and not self.df.empty:
            return self.summarizer.get_summary()
        return "No data loaded or summarizer not initialized, or DataFrame is empty.", []

    def get_dataframe_head(self) -> pd.DataFrame:
        """Returns the head of the loaded DataFrame for preview."""
        if self.df is not None:
            return self.df.head()
        return pd.DataFrame()
