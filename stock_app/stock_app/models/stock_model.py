from typing import List, Dict
from dataclasses import dataclass


from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData


from .utils.logger import configure_logger
from .utils.sql_utils import get_db_connection
from .portfolio_model import PortfolioModel
import sqlite3
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
    
    key = os.getenv("API_KEY")
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=' + name + '&outputsize=full&apikey=' + key

    r = requests.get(url)
    data = r.json()

    def __post_init__(self, data):
        if 'Error Message' in data:
            raise ValueError("Invalid Company Symbol")


def buy_stock(symbol: str, quantity: int, user: PortfolioModel):
    """
    Buys a specified quantity of stock. If the stock already exists in the database,
    its quantity is updated; otherwise, it fetches details and inserts the stock.
    Args:
        symbol (str): The stock symbol.
        quantity (int): The number of shares to buy.
        portfolio_model (PortfolioModel): The portfolio model for stock lookups.
    Raises:
        ValueError: If the stock data is invalid or there is an error with the database operation.
    """
    if not isinstance(symbol, str) or not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("Invalid symbol or quantity. Symbol must be a string, and quantity must be a positive integer.")
    try:
        stock_info = user.look_up_stock(symbol)
        if "error" in stock_info:
            raise ValueError(stock_info["error"])
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT quantity FROM stocks WHERE symbol = ?", (symbol,))
            existing_stock = cursor.fetchone()
            if existing_stock:
                new_quantity = existing_stock[0] + quantity
                cursor.execute(
                    "UPDATE stocks SET quantity = ?, current_price = ? WHERE symbol = ?",
                    (new_quantity, stock_info["current_price"], symbol)
                )
                logger.info("Updated stock: %s now has %d shares.", symbol, new_quantity)
            else:
                cursor.execute("""
                    INSERT INTO stocks (symbol, name, current_price, description, sector, industry, market_cap, quantity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    symbol,
                    stock_info["name"],
                    stock_info["current_price"],
                    stock_info["description"],
                    stock_info["sector"],
                    stock_info["industry"],
                    stock_info["market_cap"],
                    quantity,
                ))
                logger.info("Stock created successfully: %s - %s (%d shares).", symbol, stock_info["name"], quantity)
            conn.commit()

    except sqlite3.IntegrityError as e:
        logger.error("Stock with symbol '%s' already exists in the database.", symbol)
        raise ValueError(f"Stock with symbol '{symbol}' already exists.") from e
    except sqlite3.Error as e:
        logger.error("Database error while buying stock '%s': %s", symbol, str(e))
        raise sqlite3.Error(f"Database error: {str(e)}")
    except Exception as e:
        logger.error("Unexpected error while buying stock '%s': %s", symbol, str(e))
        raise ValueError(f"Unexpected error: {str(e)}")
    

def sell_stock(symbol: str, quantity: int):
    """
    Sells a specified quantity of stock. If quantity reaches zero, the stock is removed from the database.
    Args:
        symbol (str): The stock symbol.
        quantity (int): The number of shares to sell.
    Raises:
        ValueError: If the stock does not exist, insufficient quantity, or other database issues.
    """
    if not isinstance(symbol, str) or not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("Invalid symbol or quantity. Symbol must be a string, and quantity must be a positive integer.")
    
    try:
        # Use the context manager to handle the database connection
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Check if the stock exists in the database
            cursor.execute("SELECT quantity FROM stocks WHERE symbol = ?", (symbol,))
            existing_stock = cursor.fetchone()
            if not existing_stock:
                raise ValueError(f"Stock {symbol} not found in the portfolio.")
            current_quantity = existing_stock[0]
            if current_quantity < quantity:
                raise ValueError(f"Not enough shares to sell for {symbol}.")
            if current_quantity == quantity:
                # Remove the stock from the portfolio
                cursor.execute("DELETE FROM stocks WHERE symbol = ?", (symbol,))
                logger.info("Stock selled from portfolio: %s.", symbol)
            else:
                # Update the stock's quantity
                new_quantity = current_quantity - quantity
                cursor.execute(
                    "UPDATE stocks SET quantity = ? WHERE symbol = ?",
                    (new_quantity, symbol)
                )
                logger.info("Sold %d shares of %s. Remaining shares: %d.", quantity, symbol, new_quantity)
            conn.commit()

    except sqlite3.Error as e:
        logger.error("Database error while selling stock '%s': %s", symbol, str(e))
        raise sqlite3.Error(f"Database error: {str(e)}")
    except Exception as e:
        logger.error("Unexpected error while selling stock '%s': %s", symbol, str(e))
        raise ValueError(f"Unexpected error: {str(e)}")
