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

@patch("stock_app.models.stock_model.FundamentalData.get_company_overview", return_value=None)
@patch("stock_app.models.stock_model.TimeSeries.get_quote_endpoint", return_value=(None, None))
def test_lookup_stock_no_data(mock_get_company_overview, mock_get_quote_endpoint, mock_alpha_vantage_timeseries):
    """Test error handling when no data is found in lookup_stock."""
    with pytest.raises(ValueError, match="No data found for symbol"):
        lookup_stock("INVALID", mock_alpha_vantage_timeseries, mock_get_company_overview)


def test_get_latest_price(mock_alpha_vantage_timeseries):
    """Test retrieving the latest stock price."""
    symbol = "AAPL"
    mock_alpha_vantage_timeseries.get_quote_endpoint.return_value = (
        {"05. price": "145.00"},
        None,
    )

    price = get_latest_price(symbol, mock_alpha_vantage_timeseries)

    assert price == 145.0

@patch("stock_app.models.stock_model.TimeSeries.get_quote_endpoint", return_value=None)
def test_get_latest_price_no_data(mock_get_quote_endpoint, mock_alpha_vantage_timeseries):
    """Test error handling when no data is found in get_latest_price."""
    with pytest.raises(ValueError, match="No price data found for symbol"):
        get_latest_price("INVALID", mock_alpha_vantage_timeseries)

def test_stock_historical_data(mock_alpha_vantage_timeseries):
    """Test retrieving historical price data."""
    symbol = "AAPL"
    mock_alpha_vantage_timeseries.get_daily.return_value = (
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

@patch("stock_app.models.stock_model.TimeSeries.get_daily_adjusted", return_value=None)
def test_stock_historical_data_no_data(mock_get_daily_adjusted, mock_alpha_vantage_timeseries):
    """Test error handling when no historical data is found."""
    with pytest.raises(ValueError, match="No historical data found for symbol"):
        stock_historical_data("INVALID", mock_alpha_vantage_timeseries, size="compact")
