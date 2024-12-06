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