import pandas as pd
import io

def load_csv(file) -> pd.DataFrame:
    """Loads a CSV file into a Pandas DataFrame."""
    return pd.read_csv(file)

def load_excel(file) -> pd.DataFrame:
    """Loads an Excel file into a Pandas DataFrame."""
    return pd.read_excel(file)

def load_data(file_obj, file_type: str) -> pd.DataFrame:
    """Dispatcher for loading data based on file type."""
    if file_type == "csv":
        return load_csv(file_obj)
    elif file_type == "xlsx" or file_type == "xls":
        return load_excel(file_obj)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
