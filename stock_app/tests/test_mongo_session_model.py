import pytest

from stock_app.models.mongo_session_model import login_user, logout_user

@pytest.fixture
def sample_user_id():
    return 1  # Example user ID

@pytest.fixture
def sample_stock_holdings():
    return {
        "AAPL": {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "current_price": 150.0,
            "description": "Tech company",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "market_cap": "2T",
            "quantity": 10,
        }
    }


def test_login_user_creates_session_if_not_exists(mocker, sample_user_id):
    """Test login_user creates a session with no stock holdings if it does not exist."""
    mock_find = mocker.patch("stock_app.clients.mongo_client.sessions_collection.find_one", return_value=None)
    mock_insert = mocker.patch("stock_app.clients.mongo_client.sessions_collection.insert_one")
    mock_portfolio_model = mocker.Mock()

    login_user(sample_user_id, mock_portfolio_model)

    mock_find.assert_called_once_with({"user_id": sample_user_id})
    mock_insert.assert_called_once_with({"user_id": sample_user_id, "stock_holdings": {}, "funds": 0.0})
    mock_portfolio_model.clear_all_stocks.assert_not_called()
    mock_portfolio_model.load_stock.assert_not_called()

def test_login_user_loads_stocks_if_session_exists(mocker, sample_user_id):
    """Test login_user loads stocks if session exists."""
    mock_find = mocker.patch(
        "stock_app.clients.mongo_client.sessions_collection.find_one",
        return_value={
            "user_id": sample_user_id,
            "stock_holdings": {
                "AAPL": {
                    "symbol": "AAPL",
                    "name": "Apple Inc.",
                    "current_price": 150.0,
                    "description": "Tech company",
                    "sector": "Technology",
                    "industry": "Consumer Electronics",
                    "market_cap": "2T",
                    "quantity": 10,
                }
            },
            "funds": 1000.0,
        }
    )
    mock_portfolio_model = mocker.Mock()

    login_user(sample_user_id, mock_portfolio_model)

    mock_find.assert_called_once_with({"user_id": sample_user_id})
    mock_portfolio_model.clear_all_stocks.assert_called_once()
    mock_portfolio_model.profile_charge_funds.assert_called_once_with(1000.0)
    mock_portfolio_model.load_stock.assert_called_once()


def test_logout_user_updates_stocks(mocker, sample_user_id):
    """Test logout_user updates the stock holdings in the session."""
    mock_update = mocker.patch("stock_app.clients.mongo_client.sessions_collection.update_one", return_value=mocker.Mock(matched_count=1))
    mock_portfolio_model = mocker.Mock()

    # Mock the stock holdings to return objects with attributes like a Stock
    mock_stock = mocker.Mock()
    mock_stock.symbol = "AAPL"
    mock_stock.name = "Apple Inc."
    mock_stock.current_price = 150.0
    mock_stock.description = "Tech company"
    mock_stock.sector = "Technology"
    mock_stock.industry = "Consumer Electronics"
    mock_stock.market_cap = "2T"
    mock_stock.quantity = 10

    mock_portfolio_model.get_stock_holdings.return_value = {"AAPL": mock_stock}
    mock_portfolio_model.get_funds.return_value = 1000.0

    logout_user(sample_user_id, mock_portfolio_model)

    mock_update.assert_called_once_with(
        {"user_id": sample_user_id},
        {
            "$set": {
                "stock_holdings": {
                    "AAPL": {
                        "symbol": "AAPL",
                        "name": "Apple Inc.",
                        "current_price": 150.0,
                        "description": "Tech company",
                        "sector": "Technology",
                        "industry": "Consumer Electronics",
                        "market_cap": "2T",
                        "quantity": 10,
                    }
                },
                "funds": 1000.0,
            }
        },
        upsert=False
    )
    mock_portfolio_model.clear_all_stocks.assert_called_once()


def test_logout_user_raises_value_error_if_no_user(mocker, sample_user_id):
    """Test logout_user raises ValueError if no session document exists."""
    mock_update = mocker.patch("stock_app.clients.mongo_client.sessions_collection.update_one", return_value=mocker.Mock(matched_count=0))
    mock_portfolio_model = mocker.Mock()

    # Mock get_stock_holdings to return an empty dictionary
    mock_portfolio_model.get_stock_holdings.return_value = {}
    mock_portfolio_model.get_funds.return_value = 0.0

    with pytest.raises(ValueError, match=f"User with ID {sample_user_id} not found for logout."):
        logout_user(sample_user_id, mock_portfolio_model)

    mock_update.assert_called_once_with(
        {"user_id": sample_user_id},
        {"$set": {"stock_holdings": {}, "funds": 0.0}},
        upsert=False
    )