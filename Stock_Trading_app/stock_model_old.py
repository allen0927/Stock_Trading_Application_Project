from dataclasses import dataclass
import logging
import sqlite3
from typing import Any

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData

from stock_collection.utils.logger import configure_logger
from stock_collection.utils.sql_utils import get_db_connection


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
        if self.current_price <= 0:
            raise ValueError(f"Duration must be greater than 0, got {self.duration}")

def buy_stock(symbol: str, quantity: int) -> None:
    """
    """
    # Validate the required fields
    if not isinstance(symbol, str):
        raise ValueError(f"Invalid symbol provided: {symbol} (must be an string symbol representing stock).")
    if not isinstance(quantity, int) or quantity <= 0:
        raise ValueError(f"Invalid quantity provided: {quantity} (must be an integer quantity representing stock shares and at least 1).")

    try:
        # Use the context manager to handle the database connection
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT quantity FROM stocks WHERE symbol = ?", (symbol,))
            existing_stock = cursor.fetchone()
            if existing_stock:
                # Stock exists, update the quantity
                new_quantity = existing_stock[0] + quantity
                cursor.execute(
                    "UPDATE stocks SET quantity = ? WHERE symbol = ?",
                    (new_quantity, symbol)
                )
                conn.commit()
                logger.info("Updated stock quantity: %s now has %d shares.", symbol, new_quantity)
            else:
                API_KEY = "7MSGPJ5N3CP2HFIW"
                ts = TimeSeries(api_key=API_KEY)
                fd = FundamentalData(api_key=API_KEY)

                # Fetch current price
                quote, _ = ts.get_quote_endpoint(symbol)
                current_price = float(quote["05. price"])

                overview, _ = fd.get_company_overview(symbol)
                name = overview.get("Name", "N/A")
                description = overview.get("Description", "N/A")
                sector = overview.get("Sector", "N/A")
                industry = overview.get("Industry", "N/A")
                market_cap = overview.get("MarketCapitalization", "N/A")

                cursor.execute("""
                    INSERT INTO stocks (symbol, name, current_price, description, sector, industry, market_cap, quantity)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (symbol, name, current_price, description, sector, industry, market_cap, quantity))
                conn.commit()

                logger.info("Stock created successfully: %s - %s (%.2f)", symbol, name, current_price)
    except sqlite3.IntegrityError as e:
        logger.error("Stock with symbol '%s', name '%s', and current_price %.2f already exists.", symbol, name, current_price)
        raise ValueError(f"Stock with symbol '{symbol}', name '{name}', and current_price {current_price} already exists.") from e
    except sqlite3.Error as e:
        logger.error("Database error while creating stock: %s", str(e))
        raise sqlite3.Error(f"Database error: {str(e)}")


def sell_stock(symbol: str) -> None:
    """
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the song exists and if it's already deleted
            cursor.execute("SELECT selled FROM stocks WHERE symbol = ?", (symbol,))
            try:
                selled = cursor.fetchone()[0]
                if selled:
                    logger.info("Stock with symbol %s has already been selled", symbol)
                    raise ValueError(f"Stock with symbol {symbol} has already been selled")
            except TypeError:
                logger.info("Stock with symbol %s not found", symbol)
                raise ValueError(f"Stock with symbol {symbol} not found")

            # Perform the soft delete by setting 'deleted' to TRUE
            cursor.execute("UPDATE stocks SET selled = TRUE WHERE symbol = ?", (symbol,))
            cursor.execute("UPDATE stocks SET quantity = 0 WHERE symbol = ?", (symbol,))
            conn.commit()

            logger.info("Stock with symbol %s marked as selled.", symbol)

    except sqlite3.Error as e:
        logger.error("Database error while selling Stock: %s", str(e))
        raise e
    
def update_stock_price(symbol: str) -> None:
    """
    !add docstring!
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the song exists and if it's already deleted
            cursor.execute("SELECT current_price FROM stocks WHERE symbol = ?", (symbol,))
            try:
                price = cursor.fetchone()[0]
                if price:
                    API_KEY = "7MSGPJ5N3CP2HFIW"
                    ts = TimeSeries(api_key=API_KEY)
                    quote, _ = ts.get_quote_endpoint(symbol)
                    updated_price = float(quote["05. price"])
                    cursor.execute("UPDATE stocks SET current_price = ? WHERE symbol = ?", (updated_price, symbol,))
                    
                    conn.commit()
                    logger.info("The price of Stock with symbol %s has been updated.", symbol)
            except TypeError:
                logger.info("Stock with symbol %s not found", symbol)
                raise ValueError(f"Stock with symbol {symbol} not found")

            # Perform the soft delete by setting 'deleted' to TRUE


    except sqlite3.Error as e:
        logger.error("Database error while selling Stock: %s", str(e))
        raise e

#有问题
def get_stock_by_symbol(symbol: str) -> Stock:
    """
        symbol: str
    name: str
    current_price: float
    description: str
    sector: str
    industry: str
    market_cap: str
    quantity: int
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to retrieve Stock with symbol %s", symbol)
            #!!!!!!!!!!!!note the stocks table needs to change or not!!!!!!!!!!!!!!
            cursor.execute("""
                SELECT symbol, name, current_price, description, sector, industry, market_cap, quantity, all_selled
                FROM stocks
                WHERE symbol = ?
            """, (symbol,))
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            row = cursor.fetchone()

            if row:
                if row[8]:  # selled flag
                    logger.info("Stock with symbol %s has been selled", symbol)
                    raise ValueError(f"Stock with symbol {symbol} has been selled")
                logger.info("Stock with symbol %s found", symbol)
                return Stock(symbol=row[0], name=row[1], current_price=row[2], description=row[3], 
                             sector=row[4], industry=row[5], market_cap=row[6], quantity=row[7])
            else:
                logger.info("Stock with symbol %s not found", symbol)
                raise ValueError(f"Stock with symbol {symbol} not found")

    except sqlite3.Error as e:
        logger.error("Database error while retrieving stock by symbol %s: %s", symbol, str(e))
        raise e
    
def get_all_stocks(sort_by_symbol_alphabetical: bool = False) -> list[dict]:
    """
    symbol: str
    name: str
    current_price: float
    description: str
    sector: str
    industry: str
    market_cap: str
    quantity: int
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to retrieve all non-deleted songs from the catalog")

            # Determine the sort order based on the 'sort_by_play_count' flag
            query = """
                SELECT symbol, name, current_price, sector, industry, market_cap, quantity
                FROM stocks
                WHERE selled = FALSE
            """
            if sort_by_symbol_alphabetical:
                query += " ORDER BY symbol DESC"

            cursor.execute(query)
            rows = cursor.fetchall()

            if not rows:
                logger.warning("The stock catalog is empty.")
                return []

            songs = [
                {
                    "symbol": row[0],
                    "name": row[1],
                    "current_price": row[2],
                    "sector": row[3],
                    "industry": row[4],
                    "market_cap": row[5],
                    "quantity": row[6],
                }
                for row in rows
            ]
            logger.info("Retrieved %d songs from the catalog", len(songs))
            return songs

    except sqlite3.Error as e:
        logger.error("Database error while retrieving all songs: %s", str(e))
        raise e

# !!!!!!!!!!!!!!!!!!Check if this is needed!!!!!!!!!!!!!!!!!
# def get_stock_description_by_symbol(symbol: str) -> str: