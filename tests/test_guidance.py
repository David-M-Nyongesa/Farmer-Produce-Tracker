from datetime import date, timedelta

import pytest

from models.grain_crop import GrainCrop
from models.harvest import HarvestRecord
from models.market_price import MarketPrice
from models.perishable_crop import PerishableCrop
from services import evaluate_offer

TODAY = date.today()
MAIZE_MARKET = 4000      # floor works out to 3400
TOMATO_MARKET = 520      # floor works out to 442

def make_maize_harvest(days_old=10):
    crop = GrainCrop("C001", "Maize", "bag", 2800, max_storage_months=12)
    return HarvestRecord("H01", "F017", crop, 20, TODAY - timedelta(days=days_old))

def make_tomato_harvest(days_old=5):
    crop = PerishableCrop("C003", "Tomato", "crate", 300, shelf_life_days=5)
    return HarvestRecord("H02", "F017", crop, 8, TODAY - timedelta(days=days_old))

def test_an_offer_at_or_above_the_market_price_means_sell():
    assert evaluate_offer(make_maize_harvest(), MAIZE_MARKET, 4100)["status"] == "sell"
    assert evaluate_offer(make_maize_harvest(), MAIZE_MARKET, 4000)["status"] == "sell"

def test_an_offer_between_the_floor_and_the_market_means_negotiate():
    assert evaluate_offer(make_maize_harvest(), MAIZE_MARKET, 3600)["status"] == "negotiate"
    assert evaluate_offer(make_maize_harvest(), MAIZE_MARKET, 3400)["status"] == "negotiate"

def test_a_low_offer_on_grain_means_hold():
    assert evaluate_offer(make_maize_harvest(), MAIZE_MARKET, 3000)["status"] == "hold"

def test_a_low_offer_on_spoiling_tomatoes_means_sell_now():
    result = evaluate_offer(make_tomato_harvest(days_old=5), TOMATO_MARKET, 380)
    assert result["status"] == "sell now"

def test_the_same_low_offer_on_fresh_tomatoes_means_hold():
    result = evaluate_offer(make_tomato_harvest(days_old=0), TOMATO_MARKET, 380)
    assert result["status"] == "hold"

def test_the_result_shows_the_numbers_and_a_message():
    result = evaluate_offer(make_maize_harvest(), MAIZE_MARKET, 3600)
    assert result["offer"] == 3600
    assert result["market"] == 4000
    assert result["floor"] == pytest.approx(3400)
    assert isinstance(result["message"], str) and result["message"] != ""

def test_an_offer_of_zero_is_rejected():
    with pytest.raises(ValueError, match="Offer must be greater than zero"):
        evaluate_offer(make_maize_harvest(), MAIZE_MARKET, 0)

def test_a_price_of_zero_is_rejected():
    with pytest.raises(ValueError, match="Price must be greater than zero"):
        MarketPrice("C001", "Meru", 0, TODAY)

def test_a_price_goes_stale_once_it_is_old_enough():
    fresh = MarketPrice("C001", "Meru", 4000, TODAY - timedelta(days=3))
    old = MarketPrice("C001", "Meru", 4000, TODAY - timedelta(days=8))
    assert fresh.is_stale() is False
    assert old.is_stale() is True
    assert old.days_old() == 8
