import pandas as pd
import numpy as np
import re
import requests
import json
import traceback
import os
import warnings
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from googletrans import Translator # For translation functionality

# Import functions and classes from the separate summarizer module
from summarizer1 import (
    read_excel_full_clean,
    read_excel_partial_clean,
    DataSummarizer
)

# For SharePoint - you'll need to install this: pip install Office365-REST-Python-Client
try:
    from office365.runtime.auth.client_credential import ClientCredential
    from office365.sharepoint.client_context import ClientContext
    sharepoint_client_available = True
except ImportError:
    warnings.warn("Office365-REST-Python-Client not found. SharePoint functionality will be simulated.")
    sharepoint_client_available = False

# --- Translation Utility ---
def translate_text(text: str, src_lang: str, dest_lang: str) -> str:
    """
    Translates text from src_lang to dest_lang using Google Translate.
    """
    try:
        translator = Translator()
        result = translator.translate(text, src=src_lang, dest=dest_lang)
        return result.text
    except Exception as e:
        return f"[Error] Translation failed: {e}"

LANGUAGES = {
    'af': 'afrikaans', 'sq': 'albanian', 'am': 'amharic', 'ar': 'arabic', 'hy': 'armenian',
    'az': 'azerbaijani', 'eu': 'basque', 'be': 'belarusian', 'bn': 'bengali', 'bs': 'bosnian',
    'bg': 'bulgarian', 'ca': 'catalan', 'ceb': 'cebuano', 'ny': 'chichewa',
    'zh-cn': 'chinese (simplified)', 'zh-tw': 'chinese (traditional)', 'co': 'corsican',
    'hr': 'croatian', 'cs': 'czech', 'da': 'danish', 'nl': 'dutch', 'en': 'english',
    'eo': 'esperanto', 'et': 'estonian', 'tl': 'filipino', 'fi': 'finnish', 'fr': 'french',
    'fy': 'frisian', 'gl': 'galician', 'ka': 'georgian', 'de': 'german', 'el': 'greek',
    'gu': 'gujarati', 'ht': 'haitian creole', 'ha': 'hausa', 'haw': 'hawaiian', 'iw': 'hebrew',
    'he': 'hebrew', 'hi': 'hindi', 'hmn': 'hmong', 'hu': 'hungarian', 'is': 'icelandic',
    'ig': 'igbo', 'id': 'indonesian', 'ga': 'irish', 'it': 'italian', 'ja': 'japanese',
    'jw': 'javanese', 'kn': 'kannada', 'kk': 'kazakh', 'km': 'khmer', 'ko': 'korean',
    'ku': 'kurdish (kurmanji)', 'ky': 'kyrgyz', 'lo': 'lao', 'la': 'latin', 'lv': 'latvian',
    'lt': 'lithuanian', 'lb': 'luxembourgish', 'mk': 'macedonian', 'mg': 'malagasy',
    'ms': 'malay', 'ml': 'malayalam', 'mt': 'maltese', 'mi': 'maori', 'mr': 'marathi',
    'mn': 'mongolian', 'my': 'myanmar (burmese)', 'ne': 'nepali', 'no': 'norwegian',
    'or': 'odia', 'ps': 'pashto', 'fa': 'persian', 'pl': 'polish', 'pt': 'portuguese',
    'pa': 'punjabi', 'ro': 'romanian', 'ru': 'russian', 'sm': 'samoan', 'gd': 'scots gaelic',
    'sr': 'serbian', 'st': 'sesotho', 'sn': 'shona', 'sd': 'sindhi', 'si': 'sinhala',
    'sk': 'slovak', 'sl': 'slovenian', 'so': 'somali', 'es': 'spanish', 'su': 'sundanese',
    'sw': 'swahili', 'sv': 'swedish', 'tg': 'tajik', 'ta': 'tamil', 'te': 'telugu',
    'th': 'thai', 'tr': 'turkish', 'uk': 'ukrainian', 'ur': 'urdu', 'ug': 'uyghur',
    'uz': 'uzbek', 'vi': 'vietnamese', 'cy': 'welsh', 'xh': 'xhosa', 'yi': 'yiddish',
    'yo': 'yoruba', 'zu': 'zulu'
}

# --- Data Loading Functions (stay in backend as they are connection-specific) ---

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
        self.data_summarizer = None
        self.original_file_path = None # To store path for partial cleaning if needed

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
        Dispatches to the appropriate loading function and initializes the DataSummarizer.
        """
        try:
            self.df = None # Reset df on new load
            self.original_file_path = None # Reset path

            if data_source == "file":
                file_path = kwargs.get('file_path')
                if not file_path:
                    raise ValueError("File path must be provided for file source type.")
                self.original_file_path = file_path # Store original path

                if file_path.lower().endswith(('.xls', '.xlsx', '.csv')): # Handle CSV for full clean too
                    self.df = read_excel_full_clean(file_path) # Use full clean for initial load
                else:
                    raise ValueError("Unsupported file type. Only .csv, .xls, .xlsx are supported.")
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

            # Once data is loaded and initially cleaned, initialize the DataSummarizer
            if self.df is not None and not self.df.empty:
                self.data_summarizer = DataSummarizer(self.df)
            else:
                self.data_summarizer = None

            return self.df # Return the loaded DataFrame for preview in GUI

        except Exception as e:
            self.df = None
            self.data_summarizer = None
            raise e

    def get_data_summary(self) -> tuple[str, list]:
        """
        Delegates the summarization and plotting task to the DataSummarizer instance.
        """
        if self.data_summarizer and self.df is not None and not self.df.empty:
            return self.data_summarizer.get_summary()
        return "No data loaded or summarizer not initialized, or DataFrame is empty.", []

    def analyse_dataframe(self, df: pd.DataFrame, user_prompt: str, model="deepseek/deepseek-r1:free"):
        """
        Queries the DataFrame using an LLM to generate and execute Pandas code.
        After execution, if the result is a DataFrame/Series, it's passed back to the LLM
        for natural language summarization.
        """
        # Conditionally re-load/re-clean data using partial clean for LLM
        df_for_llm = df.copy() # Default to using the already loaded df
        if self.original_file_path and (self.original_file_path.lower().endswith(('.xls', '.xlsx'))):
            try:
                # Apply partial clean specifically for the LLM query
                df_for_llm = read_excel_partial_clean(self.original_file_path)
                print("Applied partial clean for LLM query.")
            except Exception as e:
                print(f"Warning: Could not apply partial clean for LLM: {e}. Using fully cleaned df.")
                # Fallback to the fully cleaned df if partial cleaning fails

        # Build schema summary for code generation
        schema_summary = "### DataFrame Overview:\n"
        schema_summary += f"- Rows: {len(df_for_llm)}\n"
        schema_summary += f"- Columns: {len(df_for_llm.columns)}\n"

        schema_summary += "\n### Column Types:\n"
        for col in df_for_llm.columns:
            schema_summary += f"- {col}: {df_for_llm[col].dtype}\n"

        sample_rows = df_for_llm.head(3).to_dict(orient="records")
        safe_sample_rows = [
            {k: self._make_json_safe(v) for k, v in row.items()}
            for row in sample_rows
        ]
        schema_summary += "\n### Sample Rows:\n" + json.dumps(safe_sample_rows, indent=2)

        # System prompt for code generation
        code_gen_system_prompt = (
            "You are a data analyst assistant. Based on the DataFrame schema and sample rows, "
            "generate valid Pandas code that answers the user's question. "
            "Always assign the final result to a variable named `result`. "
            "Only output valid Python code. Do not return explanations or markdown formatting like ```."
        )

        messages_code_gen = [
            {"role": "system", "content": code_gen_system_prompt + "\n\n" + schema_summary},
            {"role": "user", "content": user_prompt}
        ]

        DEEPSEEK_API_KEY = "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"

        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        body_code_gen = {
            "model": model,
            "messages": messages_code_gen
        }

        try:
            # First LLM call: Generate Pandas code
            response_code_gen = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(body_code_gen))
            response_code_gen.raise_for_status()
            code = response_code_gen.json()["choices"][0]["message"]["content"].strip()

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
                "df": df_for_llm.copy(), # Use the potentially partially cleaned df
                "pd": pd,
                "np": np
            }
            exec_result = None

            # Execute the generated Pandas code
            exec(code, {"pd": pd, "np": np}, local_vars)
            exec_result = local_vars.get("result", None)

            if exec_result is None:
                # Fallback: find a suitable non-df result if 'result' variable wasn't explicitly set
                candidates = {
                    k: v for k, v in local_vars.items()
                    if k != "df" and isinstance(v, (pd.Series, pd.DataFrame, str, int, float, list, pd.Timestamp))
                }
                if candidates:
                    exec_result = list(candidates.values())[-1]

            # Format the execution result for the second LLM call (natural language generation)
            if isinstance(exec_result, pd.DataFrame):
                result_str = exec_result.to_string(index=False)
            elif isinstance(exec_result, pd.Series):
                result_str = exec_result.to_string(index=False)
            elif isinstance(exec_result, pd.Timestamp):
                result_str = exec_result.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(exec_result, (float, int, str)):
                result_str = str(exec_result)
            elif exec_result is not None:
                result_str = str(exec_result)
            else:
                return "✅ Code executed, but no explicit result to return. Check generated code for implicit actions."

            # Second LLM call: Generate natural language explanation
            nl_gen_system_prompt = (
                "You are a helpful data analyst. Explain the following data result in a concise, "
                "easy-to-understand paragraph. Focus on the key findings and avoid technical jargon "
                "unless necessary. If the result is a list of items, summarize it appropriately. "
                "Do not include any code or markdown formatting like ```."
            )
            messages_nl_gen = [
                {"role": "system", "content": nl_gen_system_prompt},
                {"role": "user", "content": f"The data analysis result is:\n{result_str}\n\nPlease explain this."}
            ]

            body_nl_gen = {
                "model": model, # Use the same model
                "messages": messages_nl_gen
            }

            response_nl_gen = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(body_nl_gen))
            response_nl_gen.raise_for_status()
            final_analysis_result = response_nl_gen.json()["choices"][0]["message"]["content"].strip()

            return final_analysis_result

        except requests.exceptions.RequestException as req_e:
            return f"❌ API Request Error: {req_e}"
        except json.JSONDecodeError as json_e:
            return f"❌ JSON Decoding Error from API: {json_e}. Response was: {response_code_gen.text if 'response_code_gen' in locals() else 'No response'}\n{traceback.format_exc()}"
        except Exception as e:
            return f"❌ Error during code execution or natural language generation:\n{str(e)}\n\n{traceback.format_exc()}"

