from typing import List, Dict
from dataclasses import dataclass

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData

from stock_app.utils.logger import configure_logger
import logging


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Stock:
    """Represents a stock with relevant attributes.

    Attributes:
        symbol (str): The stock ticker symbol.
        name (str): The name of the company.
        current_price (float): The latest fetched market price of the stock.
        description (str): A brief description of the company.
        sector (str): The sector to which the company belongs.
        industry (str): The industry of the company.
        market_cap (str): The company's market capitalization.
        quantity (int): The number of shares held (default is 0).

    Raises:
        ValueError: If `current_price` is negative.
        ValueError: If `quantity` is negative.
    """
    symbol: str
    name: str
    current_price: float
    description: str
    sector: str
    industry: str
    market_cap: str
    quantity: int

    def __post_init__(self):
        if self.current_price < 0:
            raise ValueError(f"Price must be non-negative, got {self.price}")
        if self.quantity < 0:
            raise ValueError(f"Quantity must be non-negative, got {self.quantity}")
        


def lookup_stock(symbol: str, ts: TimeSeries, fd: FundamentalData) -> dict:
    """
    Fetch detailed stock information, including the latest price.

    Args:
        symbol (str): The stock ticker symbol.
        ts (TimeSeries): An Alpha Vantage TimeSeries object for fetching stock price data.
        fd (FundamentalData): An Alpha Vantage FundamentalData object for fetching company overview.

    Returns:
        dict: A dictionary containing stock details such as symbol, name, description, 
        sector, industry, market capitalization, and current price.

    Raises:
        ValueError: If the stock symbol is invalid or no data is retrieved.
        Exception: For API or unexpected errors.
    """
    try:
        overview_data = fd.get_company_overview(symbol)
        if not overview_data or len(overview_data) < 2:
            raise ValueError(f"No data found for symbol {symbol}")

        price_data = ts.get_quote_endpoint(symbol=symbol)
        if not price_data or len(price_data) < 2 or "05. price" not in price_data[0]:
            raise ValueError(f"No price data found for symbol {symbol}")

        latest_price = float(price_data[0]["05. price"])

        return {
            "symbol": overview_data[0].get("Symbol"),
            "name": overview_data[0].get("Name"),
            "description": overview_data[0].get("Description"),
            "sector": overview_data[0].get("Sector"),
            "industry": overview_data[0].get("Industry"),
            "market_cap": overview_data[0].get("MarketCapitalization"),
            "current_price": latest_price,
        }
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching stock details: {e}")
        raise ValueError(f"Unexpected error: {str(e)}")


def get_stock_by_symbol(symbol: str, ts: TimeSeries, fd: FundamentalData) -> Stock:
    """
    Retrieve detailed stock information from API call and store as a `Stock` object.

    Args:
        symbol (str): The stock ticker symbol.
        ts (TimeSeries): An Alpha Vantage TimeSeries object for fetching stock price data.
        fd (FundamentalData): An Alpha Vantage FundamentalData object for fetching company overview.

    Returns:
        Stock: A `Stock` object containing detailed information about the stock.

    Raises:
        ValueError: If the stock symbol is invalid or no data is retrieved.
        Exception: For API or unexpected errors.
    """
    try:
        stock_info = lookup_stock(symbol, ts, fd)
        return Stock(
            symbol = stock_info["symbol"],
            name = stock_info["name"],
            current_price = stock_info["current_price"],
            description = stock_info["description"],
            sector = stock_info["sector"],
            industry = stock_info["industry"],
            market_cap = stock_info["market_cap"],
            quantity = 0
        )
    except Exception as e:
        logger.error(f"Error fetching stock data for symbol {symbol}: {e}")
        raise ValueError(f"Unexpected error: {str(e)}")


def stock_historical_data(symbol: str, ts: TimeSeries, size: str) -> list[dict]:
    """
    Fetch historical price data for a stock.

    Args:
        symbol (str): The stock ticker symbol.
        ts (TimeSeries): An Alpha Vantage TimeSeries object for fetching stock data.
        size (str): The size of the data set to retrieve ('compact' or 'full').

    Returns:
        list[dict]: A list of dictionaries, each containing historical price data, 
        including the date, open, high, low, and close prices.

    Raises:
        ValueError: If no historical data is found for the stock symbol.
        Exception: For API or unexpected errors.
    """
    try:
        data = ts.get_daily_adjusted(symbol=symbol, outputsize=size)
        if not data or len(data) < 2:
            raise ValueError(f"No historical data found for symbol {symbol}")

        historical_data = []
        for date, stats in data[0].items():
            historical_data.append({
                "date": date,
                "open": float(stats["1. open"]),
                "high": float(stats["2. high"]),
                "low": float(stats["3. low"]),
                "close": float(stats["4. close"]),
            })
        return historical_data
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching historical stock data: {e}")
        raise ValueError(f"Unexpected error: {str(e)}")


def get_latest_price(symbol: str, ts: TimeSeries) -> float:
    """
    Retrieve the latest market price for a specific stock.

    Args:
        symbol (str): The stock ticker symbol.
        ts (TimeSeries): An Alpha Vantage TimeSeries object for fetching stock data.

    Returns:
        float: The latest market price of the stock.

    Raises:
        ValueError: If no price data is found for the stock symbol.
        Exception: For API or unexpected errors.
    """
    try:
        data = ts.get_quote_endpoint(symbol=symbol)
        if not data or len(data) < 2:
            raise ValueError(f"No price data found for symbol {symbol}")

        return float(data[0].get("05. price", -1))
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching stock price: {e}")
        raise ValueError(f"Unexpected error: {str(e)}")
