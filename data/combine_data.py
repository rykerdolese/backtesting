import pandas as pd

def merge_with_sentiment(stock_df: pd.DataFrame, sentiment_path: str, output_path: str) -> None:
    """
    Merges a stock DataFrame with a sentiment DataFrame on the "Date" column and saves the result.
    """
    # Load the sentiment data
    fng_df = pd.read_csv(sentiment_path)
    
    # Merge on "Date" column, keeping only matching dates
    combined_df = pd.merge(stock_df, fng_df, on="Date", how="inner")
    
    # Save the merged DataFrame without the index
    combined_df.to_csv(output_path, index=False)


if __name__ == "__main__":
    stocks = [
        "AAPL", "MSFT", "NVDA", "GOOG", "AMZN",
        "META", "BRK-B", "LLY", "AVGO", "TSLA",
        "WMT", "JPM", "V", "UNH", "XOM",
        "ORCL", "MA", "HD", "PG", "COST",
        "^SPX"
    ]
    for stock in stocks:
        stock_df = pd.read_csv(f"./data/us_stock/{stock}.csv")
        merge_with_sentiment(stock_df, 
                            "./data/sentiment/sentiment.csv", 
                            f"./data/us_stock/all_{stock}.csv")
