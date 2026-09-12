from datetime import date

import pytest

from models.grain_crop import GrainCrop
from models.harvest import HarvestRecord
from models.perishable_crop import PerishableCrop
from services import farmer_summary, regional_totals, sales_below_floor

TODAY = date.today()
MARKET = {"C001": 4000, "C003": 520}      # floors work out to 3400 and 442

def make_maize_harvest(harvest_id, farmer_id, quantity):
    crop = GrainCrop("C001", "Maize", "bag", 2800, max_storage_months=12)
    return HarvestRecord(harvest_id, farmer_id, crop, quantity, TODAY)

def make_tomato_harvest(harvest_id, farmer_id, quantity):
    crop = PerishableCrop("C003", "Tomato", "crate", 300, shelf_life_days=5)
    return HarvestRecord(harvest_id, farmer_id, crop, quantity, TODAY)

def make_harvests():
    njeri_maize = make_maize_harvest("H01", "F017", 35)
    njeri_maize.sell(12, price=3600, buyer="Broker Ali")
    kamau_maize = make_maize_harvest("H02", "F018", 25)
    kamau_maize.sell(20, price=3200, buyer="Broker Ali")
    njeri_tomato = make_tomato_harvest("H03", "F017", 8)
    return [njeri_maize, kamau_maize, njeri_tomato]

def test_the_summary_covers_only_that_farmer():
    summary = farmer_summary(make_harvests(), "F017")
    assert summary["total_harvested"] == 43
    assert summary["total_sold"] == 12
    assert summary["still_available"] == 31

def test_a_farmer_with_nothing_gets_zeros():
    summary = farmer_summary(make_harvests(), "F999")
    assert summary == {"total_harvested": 0, "total_sold": 0, "still_available": 0}

def test_regional_totals_add_up_each_crop():
    totals = regional_totals(make_harvests())
    assert totals["Maize"] == 60
    assert totals["Tomato"] == 8
    assert regional_totals([]) == {}

def test_only_sales_under_the_floor_are_listed_with_the_shortfall():
    low = sales_below_floor(make_harvests(), MARKET)
    assert len(low) == 1
    assert low[0]["harvest_id"] == "H02"
    assert low[0]["farmer_id"] == "F018"
    assert low[0]["crop"] == "Maize"
    assert low[0]["price"] == 3200
    assert low[0]["quantity"] == 20
    assert low[0]["shortfall"] == pytest.approx(200)

def test_nothing_is_listed_when_every_sale_was_fair():
    harvest = make_maize_harvest("H04", "F017", 10)
    harvest.sell(10, price=3900, buyer="Broker Ali")
    assert sales_below_floor([harvest], MARKET) == []

def test_a_crop_with_no_published_price_is_skipped():
    harvest = make_maize_harvest("H05", "F017", 10)
    harvest.sell(10, price=100, buyer="Broker Ali")
    assert sales_below_floor([harvest], {}) == []
