import logging
from typing import Any, List

from stock_app.clients.mongo_client import sessions_collection
from stock_app.utils.logger import configure_logger
from stock_app.models.stock_model import Stock
from stock_app.models.portfolio_model import PortfolioModel


logger = logging.getLogger(__name__)
configure_logger(logger)


def login_user(user_id: int, portfolio_model) -> None:
    """
    Logs in a user by loading their session data from MongoDB.

    If a session document exists for the given `user_id`, it loads the user's 
    portfolio data (stock holdings and funds) into the provided `portfolio_model`. 
    If no session is found, a new session document is created in MongoDB with 
    an empty stock holdings list and zero funds.

    Args:
        user_id (int): The ID of the user whose session is to be loaded.
        portfolio_model: An instance of `PortfolioModel` to populate with the user's data.

    Raises:
        ValueError: If an error occurs while interacting with MongoDB.
    """
    logger.info("Attempting to log in user with ID %d.", user_id)
    session = sessions_collection.find_one({"user_id": user_id})

    if session:
        logger.info("Session found for user ID %d. Loading stocks into PortfolioModel.", user_id)
        portfolio_model.clear_all_stocks()

        funds = session.get("funds", 0.0)
        portfolio_model.profile_charge_funds(funds)

        for symbol, stock_data in session.get("stock_holdings", {}):
            logger.debug("Preparing stock: %s (%s)", symbol, stock_data)

            stock = Stock(
                symbol=stock_data["symbol"],
                name=stock_data["name"],
                current_price=stock_data["current_price"],
                description=stock_data["description"],
                sector=stock_data["sector"],
                industry=stock_data["industry"],
                market_cap=stock_data["market_cap"],
                quantity=stock_data["quantity"],
            )
            
            portfolio_model.load_stock(stock)
        

        logger.info("Stocks successfully loaded for user ID %d.", user_id)
    else:
        logger.info("No session found for user ID %d. Creating a new session with empty stock holding list.", user_id)
        sessions_collection.insert_one({"user_id": user_id, "stock_holdings": {}, "funds": 0.0})
        logger.info("New session created for user ID %d.", user_id)

def logout_user(user_id: int, portfolio_model) -> None:
    """
    Logs out a user by saving their portfolio data to MongoDB.

    Retrieves the user's current portfolio (stocks and funds) from the 
    `portfolio_model` and updates the corresponding MongoDB session document. 
    Clears the user's portfolio in `portfolio_model` after saving.

    Args:
        user_id (int): The ID of the user whose session data is to be saved.
        portfolio_model: An instance of `PortfolioModel` containing the user's data.

    Raises:
        ValueError: If no session document is found for the user in MongoDB.
    """
    logger.info("Attempting to log out user with ID %d.", user_id)

    stocks_data = portfolio_model.get_stock_holdings()

    stocks_dict = {
        symbol: {
            "symbol": stock.symbol,
            "name": stock.name,
            "current_price": stock.current_price,
            "description": stock.description,
            "sector": stock.sector,
            "industry": stock.industry,
            "market_cap": stock.market_cap,
            "quantity": stock.quantity,
        }
        for symbol, stock in stocks_data
    }

    funds = portfolio_model.get_funds()

    logger.debug("Serialized stock holdings for user ID %d: %s", user_id, stocks_dict)
    logger.debug("Serialized funds for user ID %d: %f", user_id, funds)

    result = sessions_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "stock_holdings": stocks_dict,
                "funds": funds
            }
        },
        upsert=False
    )

    if result.matched_count == 0:
        logger.error("No session found for user ID %d. Logout failed.", user_id)
        raise ValueError(f"User with ID {user_id} not found for logout.")

    logger.info("Stock holdings and funds successfully saved for user ID %d. Clearing PortfolioModel stocks.", user_id)

    portfolio_model.clear_all_stocks()
    logger.info("PortfolioModel stocks cleared for user ID %d.", user_id)
