import re

# Useful when working with multiple files (e.g., AAPL.csv or TSLA.csv) to get the ticker.
def extract_ticker_from_path(file_path: str) -> str:
    """
    Extracts the ticker symbol from the given file path.
    """
    match = re.search(r"/([^/]+)\.csv$", file_path)
    if match:
        return match.group(1)
    else:
        raise ValueError("Ticker symbol not found in the file path")