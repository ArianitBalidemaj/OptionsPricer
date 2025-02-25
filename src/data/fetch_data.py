import yfinance as yf
import pandas as pd

def get_stock_data(ticker: str, period="1y", interval="1d"):
    """
    Fetches historical stock price data for a given ticker
    
    Args:
        ticker (str): Stock ticker symbol
        period (str): Time range (e.g., "1y" for 1 year)
        interval (str): Data interval (e.g., "1d" for daily prices)

    Returns:
        pd.DataFrame: DataFrame containing historical stock price data
    """
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period, interval=interval)


    if hist.empty:
        raise ValueError(f"No data found for {ticker}")
    
    hist.reset_index(inplace=True)
    return hist

def get_options_chain(ticker: str):
    """
    Retrieves the options chain for the given stock ticker
    
    Args:
        ticker (str): Stock ticker symbol (e.g., "AAPL")
    
    Returns:
        dict: A dictionary with expiration dates as keys and call/put DataFrames
    """
    stock = yf.Ticker(ticker)
    expirations = stock.options  

    if not expirations:
        raise ValueError(f"No options data found for {ticker}")

    options_data = {}
    for exp in expirations:
        try:
            calls = stock.option_chain(exp).calls
            puts = stock.option_chain(exp).puts
            options_data[exp] = {"calls": calls, "puts": puts}
        except Exception as e:
            print(f"Error fetching options for {ticker} on {exp}: {e}")

    return options_data


