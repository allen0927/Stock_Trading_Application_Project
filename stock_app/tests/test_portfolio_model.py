import pytest
from unittest.mock import MagicMock, patch
from stock_app.models.portfolio_model import PortfolioModel
from stock_app.models.stock_model import Stock

@pytest.fixture
def portfolio():
    """Fixture for PortfolioModel."""
    return PortfolioModel(funds=1000.0, userid=1)

@pytest.fixture
def mock_alpha_vantage_timeseries():
    """Fixture to mock the Alpha Vantage TimeSeries object."""
    return MagicMock()

@pytest.fixture
def mock_alpha_vantage_fundamentaldata():
    """Fixture to mock the Alpha Vantage FundamentalData object."""
    return MagicMock()

def test_add_funds(portfolio):
    """Test adding funds to the portfolio."""
    portfolio.profile_charge_funds(500.0)
    assert portfolio.get_funds() == 1500.0

def test_add_negative_funds(portfolio):
    """Test that adding negative funds raises a ValueError."""
    with pytest.raises(ValueError, match="Funds to add must be non-negative."):
        portfolio.profile_charge_funds(-500.0)

def test_display_portfolio(portfolio):
    """Test displaying portfolio details."""
    portfolio.holding_stocks = {
        "AAPL": Stock(
            symbol="AAPL", name="Apple Inc.", current_price=150.0, quantity=10,
            description="", sector="", industry="", market_cap=""),
        "MSFT": Stock(
            symbol="MSFT", name="Microsoft Corp.", current_price=300.0, quantity=5,
            description="", sector="", industry="", market_cap="")
    }
    result = portfolio.display_portfolio()

    expected = {
        "portfolio": [
            {"symbol": "AAPL", "name": "Apple Inc.", "quantity": 10, "current_price": 150.0, "total_value": 1500.0},
            {"symbol": "MSFT", "name": "Microsoft Corp.", "quantity": 5, "current_price": 300.0, "total_value": 1500.0},
        ],
        "total_value": 1000.0 + 1500.0 + 1500.0
    }
    assert result == expected

@patch("stock_app.models.portfolio_model.lookup_stock")
def test_look_up_stock(mock_lookup_stock, portfolio):
    """Test looking up a stock's details."""
    mock_lookup_stock.return_value = {
        "symbol": "AAPL", "name": "Apple Inc.", "description": "Technology company",
        "sector": "Technology", "industry": "Consumer Electronics", "market_cap": "2500000000000"
    }
    result = portfolio.look_up_stock("AAPL")
    assert result["symbol"] == "AAPL"
    assert result["name"] == "Apple Inc."
    assert result["description"] == "Technology company"
    assert result["sector"] == "Technology"
    assert result["industry"] == "Consumer Electronics"
    assert result["market_cap"] == "2500000000000"

@patch("stock_app.models.portfolio_model.get_latest_price", return_value=200.0)
def test_update_latest_price(mock_get_latest_price, portfolio):
    """Test updating the latest price of a stock."""
    portfolio.holding_stocks["AAPL"] = Stock(
        symbol="AAPL", name="Apple Inc.", current_price=150.0, quantity=10,
        description="", sector="", industry="", market_cap="")
    updated_price = portfolio.update_latest_price("AAPL")
    assert updated_price == 200.0
    assert portfolio.holding_stocks["AAPL"].current_price == 200.0

@patch("stock_app.models.portfolio_model.get_latest_price")
@patch("stock_app.models.portfolio_model.lookup_stock")
def test_buy_stock(mock_lookup_stock, mock_get_latest_price, portfolio):
    """Test buying stock updates holdings and funds."""
    # Mock the price and stock information
    mock_get_latest_price.return_value = 100.0  # Latest price per share
    mock_lookup_stock.return_value = {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "current_price": 100.0,
        "description": "Technology company",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "market_cap": "2500000000000",
    }

    # Perform the buy operation
    portfolio.buy_stock("AAPL", 5)

    # Assert stock is added to holdings with correct quantity
    assert "AAPL" in portfolio.holding_stocks
    assert portfolio.holding_stocks["AAPL"].quantity == 5

    # Assert funds are updated correctly
    assert portfolio.get_funds() == 500.0  # 1000 - (100 * 5)

@patch("stock_app.models.portfolio_model.get_latest_price", return_value=100.0)
@patch("stock_app.models.portfolio_model.lookup_stock", return_value={
    "symbol": "AAPL", "name": "Apple Inc.", "description": "", "sector": "", "industry": "", "market_cap": ""})
def test_buy_stock_insufficient_funds(mock_lookup_stock, mock_get_latest_price, portfolio):
    """Test buying stock with insufficient funds."""
    with pytest.raises(ValueError, match="Insufficient funds"):
        portfolio.buy_stock("AAPL", 15)  # 1000.0 (funds) < 100 * 15

def test_buy_stock_invalid_quantity(portfolio):
    """Test that buying stock with zero or negative quantity raises a ValueError."""
    with pytest.raises(ValueError, match="Quantity must be at least 1."):
        portfolio.buy_stock("AAPL", 0)

@patch("stock_app.models.portfolio_model.get_latest_price")
def test_sell_stock(mock_get_latest_price, portfolio):
    """Test selling stock updates holdings and funds."""
    # Add stock to the portfolio
    portfolio.holding_stocks["AAPL"] = Stock(
        symbol="AAPL",
        name="Apple Inc.",
        current_price=150.0,  # Original purchase price
        description="Tech Company",
        sector="Technology",
        industry="Consumer Electronics",
        market_cap="2500000000000",
        quantity=10,
    )

    # Mock the latest price for selling
    mock_get_latest_price.return_value = 200.0  # Selling price per share

    # Perform the sell operation
    portfolio.sell_stock("AAPL", 5)

    # Assert remaining quantity in holdings
    assert portfolio.holding_stocks["AAPL"].quantity == 5

    # Assert funds are updated correctly
    assert portfolio.get_funds() == 1000.0 + (200.0 * 5)  # Initial funds + (price * quantity)

def test_sell_nonexistent_stock(portfolio):
    """Test that selling a stock not in portfolio raises a ValueError."""
    with pytest.raises(ValueError, match="Stock AAPL is not in your portfolio."):
        portfolio.sell_stock("AAPL", 1)

@patch("stock_app.models.portfolio_model.get_latest_price", return_value=100.0)
def test_sell_stock_exceeds_quantity(mock_get_latest_price, portfolio):
    """Test that selling more stock than owned raises a ValueError."""
    portfolio.holding_stocks["AAPL"] = Stock(
        symbol="AAPL", name="Apple Inc.", current_price=100.0, quantity=5,
        description="", sector="", industry="", market_cap="")
    with pytest.raises(ValueError, match="Not enough shares to sell"):
        portfolio.sell_stock("AAPL", 10)

def test_remove_nonexistent_stock(portfolio):
    """Test that removing a stock not in holdings raises a ValueError."""
    with pytest.raises(ValueError, match="Stock AAPL is not in your holdings."):
        portfolio.remove_interested_stock("AAPL")


def test_clear_all_stocks(portfolio):
    """Test clearing all stocks."""
    portfolio.holding_stocks = {
        "AAPL": Stock(symbol="AAPL", name="Apple Inc.", current_price=150.0, quantity=10,
                      description="", sector="", industry="", market_cap=""),
        "MSFT": Stock(symbol="MSFT", name="Microsoft Corp.", current_price=300.0, quantity=5,
                      description="", sector="", industry="", market_cap="")
    }
    portfolio.clear_all_stocks()
    assert len(portfolio.holding_stocks) == 0
    assert portfolio.get_funds() == 0.0

def test_calculate_portfolio_value(portfolio):
    """Test calculating total portfolio value."""
    # Set up initial holdings
    portfolio.holding_stocks = {
        "AAPL": Stock(
            symbol="AAPL",
            name="Apple Inc.",
            current_price=150.0,  # Price per share
            description="Tech Company",
            sector="Technology",
            industry="Consumer Electronics",
            market_cap="2500000000000",
            quantity=10,
        ),
        "MSFT": Stock(
            symbol="MSFT",
            name="Microsoft Corp.",
            current_price=300.0,  # Price per share
            description="Software Company",
            sector="Technology",
            industry="Software",
            market_cap="2000000000000",
            quantity=5,
        ),
    }

    # Calculate the total portfolio value
    total_value = portfolio.calculate_portfolio_value()

    # Assert total value includes holdings' current prices and quantities
    assert total_value == 1000.0 + (150.0 * 10) + (300.0 * 5)  # AAPL (150*10) + MSFT (300*5)

def test_calculate_asset_value(portfolio):
    """Test calculating the asset value of the portfolio."""
    portfolio.holding_stocks = {
        "AAPL": Stock(symbol="AAPL", name="Apple Inc.", current_price=150.0, quantity=10,
                      description="", sector="", industry="", market_cap=""),
        "MSFT": Stock(symbol="MSFT", name="Microsoft Corp.", current_price=300.0, quantity=5,
                      description="", sector="", industry="", market_cap="")
    }
    total_value = portfolio.calculate_asset_value()
    assert total_value == (150.0 * 10) + (300.0 * 5)

def test_load_stock(portfolio):
    """Test loading a stock into the portfolio."""
    stock = Stock(symbol="AAPL", name="Apple Inc.", current_price=150.0, quantity=10,
                  description="", sector="", industry="", market_cap="")
    portfolio.load_stock(stock)

    assert "AAPL" in portfolio.holding_stocks
    assert portfolio.holding_stocks["AAPL"].quantity == 10

    # Load the same stock again to update quantity
    stock_new = Stock(symbol="AAPL", name="Apple Inc.", current_price=150.0, quantity=5,
                      description="", sector="", industry="", market_cap="")
    portfolio.load_stock(stock_new)

    assert portfolio.holding_stocks["AAPL"].quantity == 15  # Updated quantity