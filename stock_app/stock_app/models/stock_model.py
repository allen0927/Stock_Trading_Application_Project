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


def lookup_stock(symbol: str, ts: TimeSeries, fd: FundamentalData) -> dict:
    """
    Get detailed information about a specific stock, including its latest price.
    
    Args:
        symbol (str): The stock's ticker symbol.
        ts (TimeSeries): Alpha Vantage TimeSeries object from user portfolio.
        fd (FundamentalData): Alpha Vantage FundamentalData object from user portfolio.

    Returns:
        dict: A dictionary containing stock details and the latest price.

    Raises:
        ValueError: If the stock symbol is invalid or no data is found.
        Exception: For any other issues with the API.
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
    Retrieves detailed stock information using the Alpha Vantage API.

    Args:
        symbol (str): The stock's ticker symbol.
        ts (TimeSeries): Alpha Vantage TimeSeries object.
        fd (FundamentalData): Alpha Vantage FundamentalData object.

    Returns:
        Stock: A Stock object representing the requested stock.

    Raises:
        ValueError: If the stock symbol is invalid or no data is found.
        Exception: For any other issues with the API.
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
    Get historical price data for a stock within a specified date range.
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
    Get the latest market price of a specific stock.
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
