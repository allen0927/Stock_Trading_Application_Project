import time

import pytest

from stock_app.models.portfolio_model import PortfolioModel


@pytest.fixture
def portfolio_model():
    """Fixture to provide a new instance of PortfolioModel for each test."""
    return PortfolioModel()

# Fixtures providing sample meals as dictionaries
@pytest.fixture
def sample_stock1():
    return {
        "symbol": "AAPL",
        "name": "Apple INC.",
        "current_price": 102.39,
        "description": "a certain fruit company :P",
        "sector": "idk teck maybe",
        "industry": "teck ig",
        "market_cap": "whats a market cap lol",
        "quantity": 39
    }

@pytest.fixture
def sample_stock2():
    return {
        "symbol": "BA",
        "name": "The Boeing Company",
        "current_price": 78.79,
        "description": "stop crashing planes lol",
        "sector": "helikopter",
        "industry": "manufacturing..?",
        "market_cap": "boeing cap",
        "quantity": 39
    }

@pytest.fixture
def sample_portfolio():
    return [sample_stock1, sample_stock1]



##########################################################
# Combatant Prep
##########################################################

def test_clear_combatants(portfolio_model, sample_combatants):
    """Test that clear_combatants empties the combatants list."""
    portfolio_model.combatants.extend(sample_combatants)

    # Call the clear_combatants method
    portfolio_model.clear_combatants()

    # Assert that the combatants list is now empty
    assert len(portfolio_model.combatants) == 0, "Combatants list should be empty after calling clear_combatants."

def test_clear_combatants_empty(portfolio_model):
    """Test that calling clear_combatants on an empty list works."""

    # Call the clear_combatants method with an empty list
    portfolio_model.clear_combatants()

    # Assert that the combatants list is still empty
    assert len(portfolio_model.combatants) == 0, "Combatants list should remain empty if it was already empty."

def test_get_combatants_empty(portfolio_model):
    """Test that get_combatants returns an empty list when there are no combatants."""

    # Call the function and verify the result
    combatants = portfolio_model.get_combatants()
    assert combatants == [], "Expected get_combatants to return an empty list when there are no combatants."

def test_get_combatants_with_data(portfolio_model, sample_combatants):
    """Test that get_combatants returns the correct list when there are combatants."""

    portfolio_model.combatants.extend(sample_combatants)

    # Call the function and verify the result
    combatants = portfolio_model.get_combatants()
    assert combatants == portfolio_model.combatants, "Expected get_combatants to return the correct combatants list."

def test_prep_combatant(portfolio_model, sample_meal1):
    """Test that a combatant is correctly added to the list."""

    # Call prep_combatant with the combatant data
    portfolio_model.prep_combatant(sample_meal1)

    # Assert that the combatant was added to the list
    assert len(portfolio_model.combatants) == 1, "Combatants list should contain one combatant after calling prep_combatant."
    assert portfolio_model.meals_cache[portfolio_model.combatants[0]]["meal"] == "Spaghetti", "Expected 'Spaghetti' in the combatants list."

def test_prep_combatant_full(portfolio_model, sample_combatants):
    """Test that prep_combatant raises an error when the list is full."""

    # Mock the combatants list with 2 combatants
    portfolio_model.combatants.extend(sample_combatants)

    # Define the combatant data to be passed to prep_combatant
    combatant_data = {"id": 3, "meal": "Burger", "cuisine": "American", "price": 10.0, "difficulty": "MED"}

    # Call prep_combatant and expect an error since the list is full
    with pytest.raises(ValueError, match="Combatant list is full"):
        portfolio_model.prep_combatant(combatant_data)

    # Assert that the combatants list still contains only the original 2 combatants
    assert len(portfolio_model.combatants) == 2, "Combatants list should still contain only 2 combatants after trying to add a third."


##########################################################
# Battle
##########################################################

def test_get_battle_score(portfolio_model, sample_meal1, sample_meal2):
    """Test the get_battle_score method."""

    """Test combatant 1"""
    combatant_1, combatant_2 = sample_meal1, sample_meal2
    expected_score_1 = (12.5 * 7) - 2  # 12.5 * 7 - 2 = 85.5
    assert portfolio_model.get_battle_score(combatant_1) == expected_score_1, f"Expected score: {expected_score_1}, got {portfolio_model.get_battle_score(combatant_1)}"

    expected_score_2 = (15.0 * 7) - 3  # 15.0 * 7 - 3 = 102.0
    assert portfolio_model.get_battle_score(combatant_2) == expected_score_2, f"Expected score: {expected_score_2}, got {portfolio_model.get_battle_score(combatant_2)}"

def test_battle(portfolio_model, sample_combatants, sample_meal1, sample_meal2, caplog, mocker):
    """Test the battle method with sample combatants."""

    portfolio_model.combatants.extend(sample_combatants)

    # Mock the battle functions
    mocker.patch("meal_max.models.portfolio_model.PortfolioModel.get_battle_score", side_effect=[85.5, 102.0])
    mocker.patch("meal_max.models.portfolio_model.get_random", return_value=0.42)
    mock_update_stats = mocker.patch("meal_max.models.portfolio_model.Meals.update_meal_stats")

    # Mock the TTLs to simulate unexpired cache
    portfolio_model.combatant_ttls = {
        combatant: time.time() + 60 for combatant in sample_combatants
    }

    portfolio_model.meals_cache[1] = sample_meal1
    portfolio_model.meals_cache[2] = sample_meal2

    # Call the battle method
    winner_meal = portfolio_model.battle()

    # Ensure the winner is combatant_2 since score_2 > score_1
    assert winner_meal == "Pizza", f"Expected combatant 2 to win, but got {winner_meal}"

    # Ensure update_stats was called correctly for both winner and loser
    mock_update_stats.assert_any_call(1, 'loss')  # combatant_1 is the loser
    mock_update_stats.assert_any_call(2, 'win')   # combatant_2 is the winner

    # Check that combatant_1 was removed from the combatants list
    assert len(portfolio_model.combatants) == 1, "Losing combatant was not removed from the list."
    assert portfolio_model.combatants[0] == 2, "Expected combatant 2 to remain in the list."

    # Check that the logger was called with the expected message
    assert "Two meals enter, one meal leaves!" in caplog.text, "Expected battle cry log message not found."
    assert "The winner is: Pizza" in caplog.text, "Expected winner log message not found."

def test_battle_with_empty_combatants(portfolio_model):
    """Test that the battle method raises a ValueError when there are fewer than two combatants."""

    # Call the battle method and expect a ValueError
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        portfolio_model.battle()

def test_battle_with_one_combatant(portfolio_model, sample_meal1):
    """Test that the battle method raises a ValueError when there's only one combatant."""

    # Mock the combatants list with only one combatant
    portfolio_model.combatants.append(sample_meal1)

    # Call the battle method and expect a ValueError
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        portfolio_model.battle()