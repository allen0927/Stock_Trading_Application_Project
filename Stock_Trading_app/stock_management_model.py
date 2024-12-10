import logging
import sqlite3
from typing import Dict
#path 待定
from .stock_model import StockModel, StockHolding  # Assuming StockModel is in a separate file

logger = logging.getLogger(__name__)
configure_logger(logger)


class StockManagementModel:
    def __init__(self, api_key: str):
        self.holdings: Dict[str, StockHolding] = {}
        self.stock_model = StockModel(api_key)

    def update_holding_price(self, symbol: str) -> None:
        """
        Updates the current price and total value of a holding.
        """
        stock_info = self.stock_model.get_stock_info(symbol)
        current_price = stock_info["price"]
        if symbol in self.holdings:
            self.holdings[symbol].current_price = current_price
            self.holdings[symbol].total_value = current_price * self.holdings[symbol].quantity

    def calculate_portfolio_value(self) -> float:
        """
        Calculates the total value of the user's portfolio.
        """
        for symbol in self.holdings:
            self.update_holding_price(symbol)
        return sum(holding.total_value for holding in self.holdings.values())

    def buy_stock(self, symbol: str, quantity: int) -> None:
        """
        Buys a specified quantity of stock.
        """
        stock_info = self.stock_model.get_stock_info(symbol)
        current_price = stock_info["price"]

        if symbol in self.holdings:
            self.holdings[symbol].quantity += quantity
        else:
            self.holdings[symbol] = StockHolding(
                symbol=symbol,
                quantity=quantity,
                current_price=current_price,
                total_value=current_price * quantity
            )
        self.update_holding_price(symbol)

    def sell_stock(self, symbol: str, quantity: int) -> None:
        """
        Sells a specified quantity of stock if available in holdings.
        """
        if symbol not in self.holdings or self.holdings[symbol].quantity < quantity:
            raise ValueError(f"Not enough shares to sell for {symbol}")

        self.holdings[symbol].quantity -= quantity
        if self.holdings[symbol].quantity == 0:
            del self.holdings[symbol]
        else:
            self.update_holding_price(symbol)

    def get_portfolio(self) -> Dict[str, StockHolding]:
        """
        Returns the user's portfolio holdings.
        """
        return self.holdings