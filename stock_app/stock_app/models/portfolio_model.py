"""
UserLogin
· ??....??
    ->Portfolio
    ·lookup current holding stocks
    ·Displays the user's current stock holdings: quantity, current price of each stock, and the total value of each holding
        -> StockModel
        · buy/sell stocks, modifying database
        -> UserModel
        · create, delete

StockModel 是来用api来获取stock当前行情的,然后转换成Stock的object让stock management使用

StockManagement则是执行stock的操作, 例如 买/卖/看数据...
"""
import logging
import sqlite3
from typing import List, Dict


from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
from .utils.logger import configure_logger
from .utils.sql_utils import get_db_connection

logger = logging.getLogger(__name__)
configure_logger(logger)


class PortfolioModel:
    API_KEY = "demo"  # Replace with your actual API key

    def __init__(self):
        self.ts = TimeSeries(api_key=self.API_KEY)
        self.fd = FundamentalData(api_key=self.API_KEY)
        #self.funds = 0       ???user可用资金???

    def display_portfolio(self) -> List[Dict]:
        """
        Displays the user's current stock holdings, including quantity,
        current price, total value, and overall portfolio value.
        """
        portfolio = []
        total_value = 0.0

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM stocks")
            rows = cursor.fetchall()

            for row in rows:
                stock_value = row[2] * row[7]  # current_price * quantity
                total_value += stock_value
                portfolio.append({
                    "symbol": row[0],
                    "name": row[1],
                    "current_price": row[2],
                    "quantity": row[7],
                    "total_value": stock_value,
                })

        return {"portfolio": portfolio, "total_value": total_value}

    def look_up_stock(self, symbol: str) -> Dict:
        """
        Provides detailed information about a specific stock,
        including its current price, historical price data, and company description.
        """
        try:
            # Fetch current price
            quote, _ = self.ts.get_quote_endpoint(symbol)
            current_price = float(quote["05. price"])

            # Fetch company overview
            overview, _ = self.fd.get_company_overview(symbol)
            return {
                "symbol": symbol,
                "current_price": current_price,
                "name": overview.get("Name", "N/A"),
                "description": overview.get("Description", "N/A"),
                "sector": overview.get("Sector", "N/A"),
                "industry": overview.get("Industry", "N/A"),
                "market_cap": overview.get("MarketCapitalization", "N/A"),
            }
        except Exception as e:
            return {"error": f"Error looking up stock {symbol}: {str(e)}"}
        
    
    def update_latest_price(self, symbol: str) -> float:
        """
        Retrieves the latest stock price from the Alpha Vantage API and updates the database.

        Args:
            symbol (str): The stock symbol to update.

        Returns:
            float: The latest price of the stock.

        Raises:
            ValueError: If the stock price could not be retrieved.
        """
        try:
            # Fetch the latest price from Alpha Vantage
            ts = TimeSeries(api_key=self.API_KEY)
            quote, _ = ts.get_quote_endpoint(symbol)
            latest_price = float(quote["05. price"])

            # Update the stock price in the database
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE stocks SET current_price = ? WHERE symbol = ?",
                    (latest_price, symbol)
                )
                conn.commit()

            logger.info("Updated latest price for %s: %.2f", symbol, latest_price)
            return latest_price
        except Exception as e:
            logger.error("Error retrieving or updating price for %s: %s", symbol, str(e))
            raise ValueError(f"Could not retrieve or update price for {symbol}: {str(e)}")

    def calculate_portfolio_value(self) -> float:
        """
        Calculates the total value of the user's investment portfolio in real-time,
        reflecting the latest stock prices.

        Returns:
            float: The total value of the portfolio.

        Raises:
            sqlite3.Error: If there is a database error.
        """
        total_value = 0.0

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT symbol, quantity FROM stocks")
                stocks = cursor.fetchall()

                for symbol, quantity in stocks:
                    # Retrieve and update the latest price
                    latest_price = self.update_latest_price(symbol)
                    total_value += latest_price * quantity

            logger.info("Total portfolio value calculated: %.2f", total_value)
            return total_value

        except Exception as e:
            logger.error("Error calculating portfolio value: %s", str(e))
            raise ValueError(f"Unexpected error: {str(e)}")
        
    