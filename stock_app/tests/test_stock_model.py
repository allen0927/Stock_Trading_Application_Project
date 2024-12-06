import pytest
from unittest.mock import MagicMock, patch
from stock_app.models.stock_model import Stock, lookup_stock, get_latest_price, stock_historical_data

# Patch the Alpha Vantage API initialization to use a mock API key
@pytest.fixture(autouse=True)
def mock_alpha_vantage_env():
    with patch("stock_app.models.portfolio_model.os.getenv", return_value="mock_api_key"):
        yield


@pytest.fixture
def mock_alpha_vantage_timeseries():
    """Fixture to mock the Alpha Vantage TimeSeries object."""
    return MagicMock()


@pytest.fixture
def mock_alpha_vantage_fundamentaldata():
    """Fixture to mock the Alpha Vantage FundamentalData object."""
    return MagicMock()


def test_lookup_stock(mock_alpha_vantage_timeseries, mock_alpha_vantage_fundamentaldata):
    """Test fetching detailed stock information."""
    symbol = "AAPL"
    mock_alpha_vantage_fundamentaldata.get_company_overview.return_value = (
        {
            "Symbol": "AAPL",
            "Name": "Apple Inc.",
            "Description": "Technology company",
            "Sector": "Technology",
            "Industry": "Consumer Electronics",
            "MarketCapitalization": "2500000000000",
        },
        None,
    )
    mock_alpha_vantage_timeseries.get_quote_endpoint.return_value = (
        {"05. price": "145.00"},
        None,
    )

    result = lookup_stock(symbol, mock_alpha_vantage_timeseries, mock_alpha_vantage_fundamentaldata)
    
    assert result["symbol"] == "AAPL"
    assert result["name"] == "Apple Inc."
    assert result["current_price"] == 145.0
    assert result["description"] == "Technology company"
    assert result["sector"] == "Technology"
    assert result["industry"] == "Consumer Electronics"
    assert result["market_cap"] == "2500000000000"


def test_get_latest_price(mock_alpha_vantage_timeseries):
    """Test retrieving the latest stock price."""
    symbol = "AAPL"
    mock_alpha_vantage_timeseries.get_quote_endpoint.return_value = (
        {"05. price": "145.00"},
        None,
    )

    price = get_latest_price(symbol, mock_alpha_vantage_timeseries)

    assert price == 145.0


def test_stock_historical_data(mock_alpha_vantage_timeseries):
    """Test retrieving historical price data."""
    symbol = "AAPL"
    mock_alpha_vantage_timeseries.get_daily_adjusted.return_value = (
        {
            "2023-12-01": {
                "1. open": "150.00",
                "2. high": "155.00",
                "3. low": "149.00",
                "4. close": "152.00",
            },
            "2023-12-02": {
                "1. open": "152.00",
                "2. high": "158.00",
                "3. low": "151.00",
                "4. close": "157.00",
            },
        },
        None,
    )

    data = stock_historical_data(symbol, mock_alpha_vantage_timeseries, size="compact")

    assert len(data) == 2
    assert data[0]["date"] == "2023-12-01"
    assert data[0]["open"] == 150.0
    assert data[0]["high"] == 155.0
    assert data[0]["low"] == 149.0
    assert data[0]["close"] == 152.0