import logging
import os
from typing import List, Dict


from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
from stock_app.models.stock_model import Stock, lookup_stock, get_latest_price
from stock_app.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


class PortfolioModel:
    API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

    def __init__(self, userid, funds):
        self.ts = TimeSeries(api_key=self.API_KEY)
        self.fd = FundamentalData(api_key=self.API_KEY)

        self.userID = userid
        self.holding_stocks: Dict[str, Stock] = {}
        self.funds = funds

    def profile_charge_funds(self, value: float) -> None:
        """
        Adds funds to the user's portfolio.
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
        Displays the user's current stock holdings, including quantity,
        current price, total value, and overall portfolio value.
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
        Provides detailed information about a specific stock,
        including its current price and company description.
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
        Retrieves the latest stock price from the Alpha Vantage API and updates the price of a Stock in holdings.

        Args:
            symbol (str): The stock symbol to update.

        Returns:
            float: The latest price of the stock.

        Raises:
            ValueError: If the stock price could not be retrieved.
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
        Calculates the total value of the user's investment portfolio in real-time,
        reflecting the latest stock prices.

        Returns:
            float: The total value of the portfolio.

        Raises:
            Exception: If there is an error calculating the value.
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
        Calculates the total value of the user's investment portfolio in real-time,
        reflecting the latest stock prices.

        Returns:
            float: The total value of the portfolio.

        Raises:
            Exception: If there is an error calculating the value.
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
        """
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")

        if symbol not in self.holding_stocks:
            raise ValueError(f"Stock {symbol} is not in your portfolio.")

        stock = self.holding_stocks[symbol]

        if stock.quantity < quantity:
            raise ValueError(f"Not enough shares to sell. Owned: {stock.quantity}, Requested: {quantity}")

        try:
            # Get the latest price
            latest_price = get_latest_price(symbol, self.ts)
            total_revenue = latest_price * quantity

            # Update stock quantity or remove it from the portfolio if all shares are sold
            stock.quantity -= quantity

            # Add the revenue to funds
            self.funds += total_revenue

            logger.info(f"Sold {quantity} shares of {symbol} at ${latest_price:.2f} each.")
        except Exception as e:
            logger.error(f"Error selling stock {symbol}: {e}")
            raise

    def add_interested_stock(self, symbol: str) -> None:
        """
        Adds a stock to the user's holdings but sets the quantity to 0.

        This method is used when the user is interested in a new stock but not buying it.

        Args:
            symbol (str): The stock's ticker symbol.

        Raises:
            ValueError: If the stock symbol is invalid or an error occurs during the API request.
        """
        try:
            if symbol in self.holding_stocks:
                raise ValueError(f"The stock {symbol} is already existed in the stocks")

            # Fetch stock details using the API
            stock_info = lookup_stock(symbol, self.ts, self.fd)
            latest_price = get_latest_price(symbol, self.ts)

            # Add stock to holdings with quantity set to 0 (or specified value)
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
        Removes a stock from the user's holdings. If the user holds any shares of this stock,
        all shares are sold before removal.

        Args:
            symbol (str): The stock's ticker symbol.

        Raises:
            ValueError: If the stock symbol is invalid or not in the user's holdings.
            Exception: If an error occurs while selling the stock or removing it.
        """
        if symbol not in self.holding_stocks:
            raise ValueError(f"Stock {symbol} is not in your holdings.")

        try:
            stock = self.holding_stocks[symbol]

            # Sell all shares of the stock if the quantity is greater than 0
            if stock.quantity > 0:
                logger.info(f"Selling all shares of {symbol} before removing it.")
                self.sell_stock(symbol, stock.quantity)

            # Remove the stock from holdings
            del self.holding_stocks[symbol]
            logger.info(f"Removed {symbol} from holdings.")
        except Exception as e:
            logger.error(f"Error removing interested stock {symbol}: {e}")
            raise