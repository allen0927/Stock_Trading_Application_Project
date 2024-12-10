import logging
import os
from typing import List, Dict
from dotenv import load_dotenv

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
from stock_app.models.stock_model import Stock, lookup_stock, get_latest_price
from stock_app.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

load_dotenv()

class PortfolioModel:
    """
    Manages a user's stock portfolio.

    This class interacts with the Alpha Vantage API to manage stocks, funds, 
    and portfolio information, providing functionalities to buy, sell, and 
    view stocks, as well as update stock prices and calculate portfolio values.

    Attributes:
        _API_KEY (str): Alpha Vantage API key, retrieved from the environment variables.
        ts (TimeSeries): TimeSeries object for fetching stock price data.
        fd (FundamentalData): FundamentalData object for fetching company data.
        userID (str): User identifier.
        holding_stocks (Dict[str, Stock]): Dictionary of stocks in the user's portfolio.
        funds (float): Available funds in the portfolio.

    Raises:
        ValueError: If the API key is not found in the environment variables.
    """
    _API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
    if not _API_KEY:
        raise ValueError("Retrieval of API key failed, check the environment variable")
    ts = TimeSeries(_API_KEY)
    fd = FundamentalData(_API_KEY)

    def __init__(self, funds=0.0, userid=None):
        """
        Initializes the PortfolioModel instance.

        Args:
            funds (float, optional): Initial funds for the portfolio. Defaults to None.
            userid (str, optional): User identifier. Defaults to None.
        """
        self.userID = userid
        self.holding_stocks: Dict[str, Stock] = {}
        self.funds = funds


    def profile_charge_funds(self, value: float) -> None:
        """
        Charge the funds to the user's portfolio, increment user's available balance.

        Args:
            value (float): The amount of funds to add.

        Raises:
            ValueError: If the value is negative.
        """
        if value < 0:
            raise ValueError("Funds to add must be non-negative.")
        self.funds += value
        logger.info(f"Funds charged: ${value:.2f}. Total funds: ${self.funds:.2f}")

    def display_portfolio(self) -> List[Dict]:
        """
        Displays the user's current stock holdings and total portfolio value.

        Returns:
            dict: A summary of the portfolio, including each stock's details and the total value.
        """
        portfolio_summary = []
        total_portfolio_value = self.funds

        for symbol, stock in self.holding_stocks.items():
            stock_value = stock.current_price * stock.quantity
            total_portfolio_value += stock_value
            portfolio_summary.append({
                "symbol": stock.symbol,
                "name": stock.name,
                "quantity": stock.quantity,
                "current_price": stock.current_price,
                "total_value": stock_value,
            })

        logger.info("Portfolio displayed.")
        return {"portfolio": portfolio_summary, "total_value": total_portfolio_value}

    def look_up_stock(self, symbol: str) -> Dict:
        """
        Fetches detailed information about a stock by calling lookup_stock function in stock_model.

        Args:
            symbol (str): The stock ticker symbol.

        Returns:
            dict: A dictionary containing stock details.

        Raises:
            Exception: If there is an error during the stock lookup.
        """
        try:
            stock_info = lookup_stock(symbol, self.ts, self.fd)
            logger.info(f"Stock information retrieved for {symbol}.")
            return stock_info
        except Exception as e:
            logger.error(f"Error looking up stock {symbol}: {e}")
            raise

    def update_latest_price(self, symbol: str) -> float:
        """
        Retrieves latest price of specified stock and updates the latest stock price in the user's holdings.

        Args:
            symbol (str): The stock ticker symbol.

        Returns:
            float: The updated latest price of the stock.

        Raises:
            ValueError: If the stock price cannot be retrieved.
        """
        try:
            latest_price = get_latest_price(symbol, self.ts)
            if symbol in self.holding_stocks:
                self.holding_stocks[symbol].current_price = latest_price
            logger.info(f"Updated latest price for {symbol}: ${latest_price:.2f}")
            return latest_price
        except Exception as e:
            logger.error(f"Error updating latest price for {symbol}: {e}")
            raise

    def calculate_portfolio_value(self) -> float:
        """
        Calculates the total portfolio value, including funds and stocks.

        Returns:
            float: The total portfolio value.

        Raises:
            Exception: If there is an error during calculation.
        """
        try:
            total_value = self.funds
            for stock in self.holding_stocks.values():
                stock_value = stock.current_price * stock.quantity
                total_value += stock_value
            logger.info(f"Total portfolio value calculated: ${total_value:.2f}")
            return total_value
        except Exception as e:
            logger.error(f"Error calculating portfolio value: {e}")
            raise

    def calculate_asset_value(self) -> float:
        """
        Calculates the total value of the user's assets in the portfolio.

        Returns:
            float: The total asset value based on current stock prices.

        Raises:
            Exception: If there is an error during calculation.
        """
        try:
            total_value = 0
            for stock in self.holding_stocks.values():
                stock_value = stock.current_price * stock.quantity
                total_value += stock_value
            logger.info(f"Total portfolio value calculated: ${total_value:.2f}")
            return total_value
        except Exception as e:
            logger.error(f"Error calculating portfolio value: {e}")
            raise


    def buy_stock(self, symbol: str, quantity: int) -> None:
        """
        Buys a specified quantity of a stock and updates the portfolio.

        Args:
            symbol (str): The stock ticker symbol.
            quantity (int): The quantity of shares to buy.

        Raises:
            ValueError: If the quantity is invalid or funds are insufficient.
            Exception: For API or unexpected errors.
        """
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")

        try:
            latest_price = get_latest_price(symbol, self.ts)
            stock_info = lookup_stock(symbol, self.ts, self.fd)

            total_cost = latest_price * quantity

            if self.funds < total_cost:
                raise ValueError(f"Insufficient funds. Required: ${total_cost:.2f}, Available: ${self.funds:.2f}")

            self.funds -= total_cost

            if symbol in self.holding_stocks:
                self.holding_stocks[symbol].quantity += quantity
                self.holding_stocks[symbol].current_price = latest_price
            else:
                self.holding_stocks[symbol] = Stock(
                    symbol=stock_info["symbol"],
                    name=stock_info["name"],
                    current_price=latest_price,
                    description=stock_info["description"],
                    sector=stock_info["sector"],
                    industry=stock_info["industry"],
                    market_cap=stock_info["market_cap"],
                    quantity=quantity,
                )
            logger.info(f"Bought {quantity} shares of {symbol} at ${latest_price:.2f} each.")
        except Exception as e:
            logger.error(f"Error buying stock {symbol}: {e}")
            raise

    def sell_stock(self, symbol: str, quantity: int) -> None:
        """
        Sells a specified quantity of a stock from the portfolio.

        Args:
            symbol (str): The stock ticker symbol.
            quantity (int): The quantity of shares to sell.

        Raises:
            ValueError: If the quantity is invalid or insufficient shares are available.
            Exception: For API or unexpected errors.
        """
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")

        if symbol not in self.holding_stocks:
            raise ValueError(f"Stock {symbol} is not in your portfolio.")

        stock = self.holding_stocks[symbol]

        if stock.quantity < quantity:
            raise ValueError(f"Not enough shares to sell. Owned: {stock.quantity}, Requested: {quantity}")

        try:
            latest_price = get_latest_price(symbol, self.ts)
            total_revenue = latest_price * quantity

            stock.quantity -= quantity

            self.funds += total_revenue

            logger.info(f"Sold {quantity} shares of {symbol} at ${latest_price:.2f} each.")
        except Exception as e:
            logger.error(f"Error selling stock {symbol}: {e}")
            raise

    def add_interested_stock(self, symbol: str) -> None:
        """
        Adds a stock to the user's portfolio with zero quantity.

        This allows the user to track a stock without holding any shares.

        Args:
            symbol (str): The stock ticker symbol.

        Raises:
            ValueError: If the stock symbol is already in the portfolio.
            Exception: For API or unexpected errors.
        """
        try:
            if symbol in self.holding_stocks:
                raise ValueError(f"The stock {symbol} is already existed in the stocks")

            stock_info = lookup_stock(symbol, self.ts, self.fd)
            latest_price = get_latest_price(symbol, self.ts)

            self.holding_stocks[symbol] = Stock(
                symbol = stock_info["symbol"],
                name = stock_info["name"],
                current_price = latest_price,
                description = stock_info["description"],
                sector = stock_info["sector"],
                industry = stock_info["industry"],
                market_cap = stock_info["market_cap"],
                quantity = 0,
            )
            logger.info(f"Added {symbol} to interested stocks.")
        except Exception as e:
            logger.error(f"Error adding interested stock {symbol}: {e}")
            raise

    def remove_interested_stock(self, symbol: str) -> None:
        """
        Removes a stock from the user's portfolio.

        If the stock has shares, they are sold before removal.

        Args:
            symbol (str): The stock ticker symbol.

        Raises:
            ValueError: If the stock is not in the portfolio.
            Exception: For API or unexpected errors.
        """
        if symbol not in self.holding_stocks:
            raise ValueError(f"Stock {symbol} is not in your holdings.")

        try:
            stock = self.holding_stocks[symbol]

            if stock.quantity > 0:
                logger.info(f"Selling all shares of {symbol} before removing it.")
                self.sell_stock(symbol, stock.quantity)

            del self.holding_stocks[symbol]
            logger.info(f"Removed {symbol} from holdings.")
        except Exception as e:
            logger.error(f"Error removing interested stock {symbol}: {e}")
            raise

    def clear_all_stocks(self) -> None:
        """
        Clear all the stocks and set the funds to 0.0
        """
        self.holding_stocks = {}
        self.funds = 0.0
        logger.info("All stocks cleared and funds reset to 0.0.")

    def load_stock(self, stock: Stock) -> None:
        """
        Adds a stock to the portfolio or updates its quantity if already present.

        This method is useful for initializing the portfolio from stored data in mongo db.

        Args:
            stock (Stock): The stock to add or update.

        Raises:
            Exception: For unexpected errors during stock loading.
        """
        if stock.symbol in self.holding_stocks:
            existing_stock = self.holding_stocks[stock.symbol]
            
            existing_stock.quantity += stock.quantity

            existing_stock.current_price = stock.current_price
            existing_stock.market_cap = stock.market_cap

            logger.info(
                "Updated stock: %s. New quantity: %d.",
                stock.symbol,
                existing_stock.quantity
            )
        else:
            self.holding_stocks[stock.symbol] = stock
            logger.info("Added new stock: %s with quantity %d.", stock.symbol, stock.quantity)

    def get_stock_holdings(self):
        """Retrieves the user's current stock holdings.

        Returns:
            Dict[str, Stock]: A dictionary of stocks in the portfolio.
        """
        return self.holding_stocks
    
    def get_funds(self):
        """
        Retrieves the current available funds in the portfolio.

        Returns:
            float: The current funds available.
        """
        return self.funds