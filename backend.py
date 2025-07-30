import pandas as pd
import numpy as np
import re
import requests
import json
import traceback
import os # Import os to access environment variables
import warnings # For SharePoint client warning
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# For SharePoint - you'll need to install this: pip install Office365-REST-Python-Client
try:
    from office365.runtime.auth.client_credential import ClientCredential
    from office365.sharepoint.client_context import ClientContext
    sharepoint_client_available = True
except ImportError:
    warnings.warn("Office365-REST-Python-Client not found. SharePoint functionality will be simulated.")
    sharepoint_client_available = False

# Import the Summarizer class from summarizer.py
from summarizer import Summarizer

# --- Utility Function for Excel Reading ---
def read_excel_clean(path: str, sheet_name: str = 0) -> pd.DataFrame:
    """
    Reads an Excel file, cleans it by dropping empty rows/columns,
    cleaning column names, inferring dtypes, and filling missing values.
    """
    df = pd.read_excel(path, sheet_name=sheet_name)

    # Step 2: Drop completely empty rows/columns
    df.dropna(how='all', inplace=True)
    df.dropna(axis=1, how='all', inplace=True)
    
   
    skip_cols = set() 
   
    df = df[[col for col in df.columns if col not in skip_cols]]

    # Step 3: Clean column names
    df.columns = [
        str(col).strip().lower().replace(' ', '_').replace('\n', '_')
        for col in df.columns
    ]

    # Step 4: Try to infer datetime columns (skip time-only formats)
    time_only_pattern = re.compile(r'^\s*\d{1,2}:\d{2}:\d{2}\s*$')

    for col in df.columns:
        if df[col].dtype == object:
            sample = df[col].dropna().astype(str).head(10)
            if not sample.empty and sample.apply(lambda x: bool(time_only_pattern.match(x))).all():
                continue  # Skip columns that look like time-only
            try:
                parsed = pd.to_datetime(df[col], errors='coerce', utc=False)
                if parsed.notna().sum() > 0.6 * len(parsed):
                    df[col] = parsed
            except Exception:
                continue

    # Step 5: Convert object-like numerics to float
    for col in df.select_dtypes(include='object').columns:
        try:
            numeric_series = pd.to_numeric(df[col], errors='coerce')
            if numeric_series.notna().sum() > 0.6 * len(numeric_series):
                df[col] = numeric_series
        except Exception:
            continue

    # Step 6: Fill missing values smartly
    for col in df.columns:
        if df[col].isna().sum() == 0:
            continue

        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].interpolate(method='linear', limit_direction='both')
            df[col] = df[col].fillna(df[col].median())
        
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].fillna(method='ffill').fillna(method='bfill')

        elif isinstance(df[col].dtype, pd.CategoricalDtype) or df[col].dtype == object:
            mode_val = df[col].mode().iloc[0] if not df[col].mode().empty else "Unknown"
            df[col] = df[col].fillna(mode_val)

    return df


def load_sql_table(dialect, username, password, host, port, database, sql_query):
    """
    Connects to a SQL database and loads data using the provided SQL query.
    Uses SQLAlchemy for database connection.
    """
    # Build the database URL
    if dialect.lower() == 'sqlite':
        database_url = f"{dialect}:///{database}"
    else:
        database_url = f"{dialect}://{username}:{password}@{host}:{port}/{database}"

    print(f"Attempting to connect to SQL database: {dialect} on {host}:{port}/{database}")
    print(f"Executing query: {sql_query}")
    

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

def load_sharepoint_list(site_url, list_name, client_id, client_secret):
    """
    Connects to a SharePoint list and loads its data into a pandas DataFrame.
    Requires Office365-REST-Python-Client and proper Azure AD App registration.
    """
    print(f"Attempting to connect to SharePoint list: '{list_name}' at '{site_url}'")
    
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


# --- Main DataAnalyzer Class ---
class DataAnalyzer:
    def __init__(self):
        self.df = None 
        self.summarizer = None 
    def _make_json_safe(self, val):
        """Helper to make values safe for JSON serialization."""
        if isinstance(val, (pd.Timestamp, pd.Timedelta, np.datetime64)):
            return str(val)
        elif pd.isna(val):
            return None
        else:
            return val

    def load_data(self, data_source: str, **kwargs):
        """
        Generic method to load data based on the source.
        Dispatches to the appropriate loading function and initializes the Summarizer.
        """
        try:
            if data_source == "file":
                
                self.df = read_excel_clean(kwargs.get('file_path'))
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
            if self.df is not None and not self.df.empty:
                self.summarizer = Summarizer(self.df) 
            else:
                self.summarizer = None
            
            return self.df # Return the loaded DataFrame for preview in GUI

        except Exception as e:
            self.df = None
            self.summarizer = None 
            raise e 

    def get_data_summary(self) -> tuple[str, list]:
        """
        Delegates the summarization and plotting task to the Summarizer instance.
        """
        if self.summarizer and self.df is not None and not self.df.empty:
            return self.summarizer.get_summary()
        return "No data loaded or summarizer not initialized, or DataFrame is empty.", []

    def analyse_dataframe(self, df: pd.DataFrame, user_prompt: str, model="deepseek/deepseek-r1:free"):
        """        Queries the DataFrame using an LLM to generate and execute Pandas code.
        This method replaces the previous 'analyse_dataframe' logic and is now part of DataAnalyzer.
        """
        # Build schema summary
        summary = "### DataFrame Overview:\n"
        summary += f"- Rows: {len(df)}\n"
        summary += f"- Columns: {len(df.columns)}\n"

        summary += "\n### Column Types:\n"
        for col in df.columns:
            summary += f"- {col}: {df[col].dtype}\n"

        sample_rows = df.head(3).to_dict(orient="records")
        safe_sample_rows = [
            {k: self._make_json_safe(v) for k, v in row.items()}
            for row in sample_rows
        ]
        summary += "\n### Sample Rows:\n" + json.dumps(safe_sample_rows, indent=2)

        # Improved system prompt
        system_prompt = (
            "You are a data analyst assistant. Based on the DataFrame schema and sample rows, "
            "generate valid Pandas code that answers the user's question. "
            "Always assign the final result to a variable named `result`. "
            "Only output valid Python code. Do not return explanations or markdown formatting like ```."
        )

        messages = [
            {"role": "system", "content": system_prompt + "\n\n" + summary},
            {"role": "user", "content": user_prompt}
        ]

       
        DEEPSEEK_API_KEY = "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" 

        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}", 
            "Content-Type": "application/json"
        }

        body = {
            "model": model,
            "messages": messages
        }

        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(body))
            response.raise_for_status() 
            code = response.json()["choices"][0]["message"]["content"].strip()
            
           
            print("\nGenerated Code:\n", code, "\n")

            # Remove any markdown code block formatting
            if code.startswith("```"):
                code = re.sub(r"^```(?:python)?\s*", "", code)
                code = re.sub(r"\s*```$", "", code)

            # Check if code is a simple expression and not already assigned to 'result'
            is_simple_expr = (
                not any(code.lstrip().startswith(kw) for kw in ["for ", "while ", "if ", "def ", "class ", "import "]) and
                "result" not in code.split("=")[0]
            )
            if is_simple_expr:
                code = f"result = {code}"

            local_vars = {
                "df": df.copy(), 
                "pd": pd,
                "np": np
            }
            result = None

            exec(code, {}, local_vars)
            result = local_vars.get("result", None)

            if result is None:
                # Fallback: find a suitable non-df result
                candidates = {
                    k: v for k, v in local_vars.items()
                    if k != "df" and isinstance(v, (pd.Series, pd.DataFrame, str, int, float, list, pd.Timestamp))
                }
                if candidates:
                    result = list(candidates.values())[-1] 

            # Format output for display
            if isinstance(result, pd.DataFrame):
                return result.to_string(index=False)
            elif isinstance(result, pd.Series):
                return result.to_string(index=False)
            elif isinstance(result, pd.Timestamp):
                return result.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(result, (float, int, str)):
                return str(result)
            elif result is not None:
                return str(result)
            else:
                return "✅ Code executed, but no explicit result to return. Check generated code for implicit actions."

        except requests.exceptions.RequestException as req_e:
            return f"❌ API Request Error: {req_e}"
        except json.JSONDecodeError as json_e:
            return f"❌ JSON Decoding Error from API: {json_e}. Response was: {response.text if 'response' in locals() else 'No response'}"
        except Exception as e:
            return f"❌ Error during code execution:\n{str(e)}\n\n{traceback.format_exc()}"
