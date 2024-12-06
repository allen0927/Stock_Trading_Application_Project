from typing import List, Dict
from dataclasses import dataclass


from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData


from .utils.logger import configure_logger
from .portfolio_model import PortfolioModel
import requests
import os
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
        overview_data, _ = fd.get_company_overview(symbol)
        if not overview_data:
            raise ValueError(f"No data found for symbol {symbol}")

        price_data, _ = ts.get_quote_endpoint(symbol=symbol)
        if not price_data or "05. price" not in price_data:
            raise ValueError(f"No price data found for symbol {symbol}")
        
        latest_price = float(price_data["05. price"])

        return {
            "symbol": overview_data.get("Symbol"),
            "name": overview_data.get("Name"),
            "description": overview_data.get("Description"),
            "sector": overview_data.get("Sector"),
            "industry": overview_data.get("Industry"),
            "market_cap": overview_data.get("MarketCapitalization"),
            "current_price": latest_price,
        }
    except Exception as e:
        logger.error(f"Error fetching stock details: {e}")
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
        data, _ = ts.get_daily_adjusted(symbol=symbol, outputsize=size)
        if not data:
            raise ValueError(f"No historical data found for symbol {symbol}")

        historical_data = []
        for date, stats in data.items():
            historical_data.append({
                "date": date,
                "open": float(stats["1. open"]),
                "high": float(stats["2. high"]),
                "low": float(stats["3. low"]),
                "close": float(stats["4. close"]),
            })
        return historical_data
    except Exception as e:
        logger.error(f"Error fetching historical stock data: {e}")
        raise ValueError(f"Unexpected error: {str(e)}")
    
def get_latest_price(symbol: str, ts: TimeSeries) -> float:
    """
    Get the latest market price of a specific stock.
    """
    try:
        data, _ = ts.get_quote_endpoint(symbol=symbol)
        if not data:
            raise ValueError(f"No price data found for symbol {symbol}")

        return float(data.get("05. price", -1))
    except Exception as e:
        logger.error(f"Error fetching stock price: {e}")
        raise ValueError(f"Unexpected error: {str(e)}")