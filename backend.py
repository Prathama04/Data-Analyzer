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

# --- Backend Functions ---

def load_excel_csv(file_path):
    """
    Loads data from an Excel (.xlsx) or CSV (.csv) file into a pandas DataFrame.
    """
    if not file_path:
        raise ValueError("No file path provided.")
    print(f"Loading file: {file_path}")
    time.sleep(1) # Simulate file loading time
    try:
        if file_path.lower().endswith('.csv'): # Use .lower() for case-insensitive check
            df = pd.read_csv(file_path)
        elif file_path.lower().endswith('.xlsx') or file_path.lower().endswith('.xls'): # Added .xls
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
    # Build the database URL
    # IMPORTANT: In a real application, do NOT hardcode credentials.
    # Use environment variables, a config file, or a secrets manager.
    if dialect.lower() == 'sqlite':
        # SQLite typically uses a file path as the database name, or ':memory:' for in-memory
        database_url = f"{dialect}:///{database}"
    else:
        # Standard format for most relational databases
        database_url = f"{dialect}://{username}:{password}@{host}:{port}/{database}"

    print(f"Attempting to connect to SQL database: {dialect} on {host}:{port}/{database}")
    print(f"Executing query: {sql_query}")
    time.sleep(2) # Simulate connection and query latency

    try:
        # Create the engine
        engine = create_engine(database_url)

        # Connect and execute query
        # Use a context manager for the connection to ensure it's closed
        with engine.connect() as connection:
            df = pd.read_sql(sql_query, connection)

        if df.empty:
            print("SQL query returned an empty DataFrame.")
            # For a real app, you might want to return an empty DF, not raise an error,
            # depending on whether an empty result is considered an "error".
            raise ValueError("No data returned for the given SQL query. Check query or database content.")

        print(f"Successfully loaded {df.shape[0]} rows from SQL database.")
        return df

    except SQLAlchemyError as e:
        # Catch specific SQLAlchemy errors for better user messages
        raise ConnectionError(f"Failed to load SQL data. Check connection details (dialect, username, password, host, port, database) and SQL query syntax. Error: {e}")
    except Exception as e:
        # Catch any other unexpected errors
        raise ConnectionError(f"An unexpected error occurred during SQL data loading: {e}")


def load_sharepoint_list(site_url, list_name, client_id, client_secret):
    """
    Connects to a SharePoint list and loads its data into a pandas DataFrame.
    Requires Office365-REST-Python-Client and proper Azure AD App registration.
    """
    print(f"Attempting to connect to SharePoint list: '{list_name}' at '{site_url}'")
    # IMPORTANT: In a real application, do NOT hardcode credentials.
    # client_secret should be handled securely, not printed or directly exposed.
    time.sleep(3) # Simulate connection and loading latency

    if not sharepoint_client_available:
        warnings.warn("Office365-REST-Python-Client not installed. Simulating SharePoint data load.")
        return _simulate_sharepoint_data(list_name)

    try:
        # Setup authentication context
        credentials = ClientCredential(client_id, client_secret)
        ctx = ClientContext(site_url).with_credentials(credentials) # Use .with_credentials()

        # Get the list and items
        sp_list = ctx.web.lists.get_by_title(list_name)
        # Execute query to get all items. For large lists, consider pagination.
        list_items = sp_list.get_items().execute_query() 

        # Extract data into a list of dictionaries
        data = [item.properties for item in list_items]

        if not data:
            print(f"SharePoint list '{list_name}' returned no data.")
            raise ValueError("SharePoint list returned no data. Check list name or permissions.")

        df = pd.DataFrame(data)
        print(f"Successfully loaded {df.shape[0]} rows from SharePoint list '{list_name}'.")
        return df

    except Exception as e:
        # Log the actual error for debugging, but provide a user-friendly message
        print(f"Failed to load real SharePoint data. Error: {e}")
        # Fallback to dummy data if real connection fails during development/testing
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


def summarize_dataframe(df: pd.DataFrame) -> str:
    """
    Generates a basic AI-like summary of the DataFrame.
    In a real application, this would involve a large language model (LLM).
    """
    if df is None or df.empty:
        return "No data available to summarize."

    print("Generating DataFrame summary...")
    time.sleep(2) # Simulate AI processing time

    num_rows, num_cols = df.shape
    columns = df.columns.tolist()
    data_types = df.dtypes.apply(lambda x: str(x)).to_dict()
    missing_values = df.isnull().sum().to_dict()

    summary = f"The dataset contains **{num_rows} rows** and **{num_cols} columns**.\n\n"
    summary += "### Columns and Data Types:\n"
    for col, dtype in data_types.items():
        summary += f"- **{col}**: {dtype}\n"

    summary += "\n### Missing Values:\n"
    if all(count == 0 for count in missing_values.values()):
        summary += "No missing values found in any column. 🎉\n"
    else:
        for col, count in missing_values.items():
            if count > 0:
                summary += f"- **{col}**: {count} missing values (**{count/num_rows:.2%}** of total)\n"

    summary += "\n### First 5 Rows:\n"
    summary += "```\n" + df.head().to_string() + "\n```"

    return summary

def analyse_dataframe(df: pd.DataFrame, prompt: str) -> str:
    """
    Simulates AI-based analysis of the DataFrame based on a user prompt.
    In a real application, this would involve sending the DataFrame schema/data
    and the prompt to a large language model (LLM) like Gemini, OpenAI GPT, etc.
    """
    if df is None or df.empty:
        return "No data available for analysis. Please load data first."

    print(f"Analyzing with prompt: {prompt}")
    response = f"AI Analysis for your query: '{prompt}'\n\n"
    time.sleep(3) # Simulate AI processing time

    prompt_lower = prompt.lower()

    # Dynamic analysis based on columns available and prompt keywords
    if "rows" in prompt_lower and ("count" in prompt_lower or "number" in prompt_lower):
        response += f"The dataset has **{df.shape[0]} rows**."
    elif "columns" in prompt_lower and ("list" in prompt_lower or "names" in prompt_lower):
        response += f"The columns in the dataset are: **{', '.join(df.columns.tolist())}**."
    elif "average" in prompt_lower or "mean" in prompt_lower:
        # Try to find a numeric column related to the prompt
        numeric_cols = df.select_dtypes(include=['number']).columns
        found_col = next((col for col in numeric_cols if col.lower() in prompt_lower), None)
        if found_col:
            avg_val = df[found_col].mean()
            response += f"The average value for **'{found_col}'** is: **{avg_val:.2f}**."
        else:
            response += "Could not find a specific numeric column for calculating average. Available numeric columns: " + ", ".join(numeric_cols.tolist()) if not numeric_cols.empty else "None."
    elif "highest" in prompt_lower or "max" in prompt_lower:
        numeric_cols = df.select_dtypes(include=['number']).columns
        found_col = next((col for col in numeric_cols if col.lower() in prompt_lower), None)
        if found_col and not df.empty:
            max_val = df[found_col].max()
            response += f"The maximum value for **'{found_col}'** is: **{max_val}**."
            # Try to get the row with max value if a 'Title' or similar column exists
            identifying_col = next((c for c in ['Title', 'product_name', 'Name', 'Item'] if c in df.columns), None)
            if identifying_col:
                max_row = df.loc[df[found_col].idxmax()]
                response += f"\nThis is associated with **'{max_row[identifying_col]}'**."
        else:
            response += "Could not find a specific numeric column or data is empty for calculating maximum."
    elif "lowest" in prompt_lower or "min" in prompt_lower:
        numeric_cols = df.select_dtypes(include=['number']).columns
        found_col = next((col for col in numeric_cols if col.lower() in prompt_lower), None)
        if found_col and not df.empty:
            min_val = df[found_col].min()
            response += f"The minimum value for **'{found_col}'** is: **{min_val}**."
            identifying_col = next((c for c in ['Title', 'product_name', 'Name', 'Item'] if c in df.columns), None)
            if identifying_col:
                min_row = df.loc[df[found_col].idxmin()]
                response += f"\nThis is associated with **'{min_row[identifying_col]}'**."
        else:
            response += "Could not find a specific numeric column or data is empty for calculating minimum."
    elif "unique" in prompt_lower and "count" in prompt_lower:
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        found_col = next((col for col in categorical_cols if col.lower() in prompt_lower), None)
        if found_col:
            unique_count = df[found_col].nunique()
            unique_values = df[found_col].unique().tolist()
            response += f"The column **'{found_col}'** has **{unique_count} unique values**: {', '.join(map(str, unique_values))}."
        else:
            response += "Could not find a specific categorical column for counting unique values. Available categorical columns: " + ", ".join(categorical_cols.tolist()) if not categorical_cols.empty else "None."
    elif "missing values" in prompt_lower:
        missing_values = df.isnull().sum()
        if missing_values.sum() == 0:
            response += "There are **no missing values** in the dataset. ✨"
        else:
            response += "Missing values per column:\n"
            for col, count in missing_values.items():
                if count > 0:
                    response += f"- **{col}**: {count} missing values (**{count/df.shape[0]:.2%}**)\n"
    elif "head" in prompt_lower or "top rows" in prompt_lower:
        response += "Here are the first few rows:\n"
        response += "```\n" + df.head().to_string() + "\n```"
    elif "tail" in prompt_lower or "bottom rows" in prompt_lower:
        response += "Here are the last few rows:\n"
        response += "```\n" + df.tail().to_string() + "\n```"
    elif "describe" in prompt_lower or "statistics" in prompt_lower:
        response += "Here are descriptive statistics for numeric columns:\n"
        response += "```\n" + df.describe().to_string() + "\n```"
    else:
        response += "I can provide insights on basic queries like 'number of rows', 'list columns', 'average [column_name]', 'highest [column_name]', 'unique [column_name] count', 'missing values', 'head', 'tail', or 'describe'. Please try a more specific question."
        response += "\n\n### DataFrame Info:\n"
        buf = io.StringIO()
        df.info(buf=buf)
        response += "```\n" + buf.getvalue() + "\n```"

    return response