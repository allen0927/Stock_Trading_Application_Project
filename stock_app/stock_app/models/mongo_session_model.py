import logging
from typing import Any, List

from stock_app.clients.mongo_client import sessions_collection
from stock_app.utils.logger import configure_logger
from stock_app.models.stock_model import Stock


logger = logging.getLogger(__name__)
configure_logger(logger)


def login_user(user_id: int, portfolio_model) -> None:
    """
    Load the user's combatants from MongoDB into the BattleModel's combatants list.

    Checks if a session document exists for the given `user_id` in MongoDB.
    If it exists, clears any current combatants in `battle_model` and loads
    the stored combatants from MongoDB into `battle_model`.

    If no session is found, it creates a new session document for the user
    with an empty combatants list in MongoDB.

    Args:
        user_id (int): The ID of the user whose session is to be loaded.
        battle_model (BattleModel): An instance of `BattleModel` where the user's combatants
                                    will be loaded.
    """
    logger.info("Attempting to log in user with ID %d.", user_id)
    session = sessions_collection.find_one({"user_id": user_id})

    if session:
        logger.info("Session found for user ID %d. Loading stocks into PortfolioModel.", user_id)
        portfolio_model.clear_all_stocks()

        # Load stock holdings from the session (default to an empty dict if missing)
        stock_holdings = session.get("stock_holdings", {})
        funds = session.get("funds", 0.0)
        portfolio_model.profile_charge_funds(funds)

        # Iterate over the stock holdings dictionary
        for symbol, stock_data in stock_holdings.items():
            logger.debug("Preparing stock: %s (%s)", symbol, stock_data)
            
            # Create a Stock object from the loaded stock data
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
            
            # Load the stock into the portfolio model
            portfolio_model.load_stock(stock)
        

        logger.info("Stocks successfully loaded for user ID %d.", user_id)
    else:
        logger.info("No session found for user ID %d. Creating a new session with empty stock holding list.", user_id)
        sessions_collection.insert_one({"user_id": user_id, "stock_holdings": {}, "funds": 0.0})
        logger.info("New session created for user ID %d.", user_id)

def logout_user(user_id: int, portfolio_model) -> None:
    """
    Store the current combatants from the BattleModel back into MongoDB.

    Retrieves the current combatants from `battle_model` and attempts to store them in
    the MongoDB session document associated with the given `user_id`. If no session
    document exists for the user, raises a `ValueError`.

    After saving the combatants to MongoDB, the combatants list in `battle_model` is
    cleared to ensure a fresh state for the next login.

    Args:
        user_id (int): The ID of the user whose session data is to be saved.
        battle_model (BattleModel): An instance of `BattleModel` from which the user's
                                    current combatants are retrieved.

    Raises:
        ValueError: If no session document is found for the user in MongoDB.
    """
    logger.info("Attempting to log out user with ID %d.", user_id)

    # Get the stock holdings from the portfolio model
    stocks_data = portfolio_model.get_stock_holdings()

    # Convert Stock objects to dictionaries for MongoDB storage
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
        for symbol, stock in stocks_data.items()
    }

    # Get the funds from the portfolio model
    funds = portfolio_model.get_funds()

    logger.debug("Serialized stock holdings for user ID %d: %s", user_id, stocks_dict)
    logger.debug("Serialized funds for user ID %d: %f", user_id, funds)

    # Update the stock_holdings and funds in the session document
    result = sessions_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "stock_holdings": stocks_dict,
                "funds": funds
            }
        },
        upsert=False  # Prevents creating a new document if not found
    )

    if result.matched_count == 0:
        logger.error("No session found for user ID %d. Logout failed.", user_id)
        raise ValueError(f"User with ID {user_id} not found for logout.")

    logger.info("Stock holdings and funds successfully saved for user ID %d. Clearing PortfolioModel stocks.", user_id)

    # Clear the portfolio model's stocks after saving
    portfolio_model.clear_all_stocks()
    logger.info("PortfolioModel stocks cleared for user ID %d.", user_id)
