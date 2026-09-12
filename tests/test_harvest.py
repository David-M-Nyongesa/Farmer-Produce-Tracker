from datetime import date, timedelta

import pytest

from models.grain_crop import GrainCrop
from models.harvest import HarvestRecord

TODAY = date.today()

def make_maize():
    return GrainCrop("C001", "Maize", "bag", 2800, max_storage_months=12)

def make_harvest(quantity=20, harvest_date=TODAY):
    return HarvestRecord("H0042", "F017", make_maize(), quantity, harvest_date)

def test_a_new_harvest_is_available_in_full():
    harvest = make_harvest(quantity=20)
    assert harvest.status == "available"
    assert harvest.quantity_available == 20

def test_a_quantity_of_zero_or_less_is_rejected():
    with pytest.raises(ValueError, match="Quantity must be greater than zero"):
        make_harvest(quantity=0)
    with pytest.raises(ValueError, match="Quantity must be greater than zero"):
        make_harvest(quantity=-5)

def test_a_harvest_dated_in_the_future_is_rejected():
    with pytest.raises(ValueError, match="Harvest date cannot be in the future"):
        make_harvest(harvest_date=TODAY + timedelta(days=6))

def test_days_since_harvest_is_counted():
    assert make_harvest(harvest_date=TODAY - timedelta(days=200)).days_since_harvest() == 200

def test_a_part_sale_is_logged_and_leaves_the_rest_available():
    harvest = make_harvest(quantity=20)
    harvest.sell(12, price=3600, buyer="Broker Ali")
    assert harvest.quantity_available == 8
    assert harvest.status == "available"
    assert harvest.sales[0] == {"quantity": 12, "price": 3600, "buyer": "Broker Ali"}

def test_selling_everything_marks_the_harvest_sold():
    harvest = make_harvest(quantity=20)
    harvest.sell(20, price=3600, buyer="Broker Ali")
    assert harvest.quantity_available == 0
    assert harvest.status == "sold"

def test_selling_more_than_is_left_is_rejected():
    harvest = make_harvest(quantity=20)
    harvest.sell(12, price=3600, buyer="Broker Ali")
    with pytest.raises(ValueError, match="Cannot sell more than the quantity available"):
        harvest.sell(10, price=3600, buyer="Broker Ali")
    assert harvest.quantity_available == 8

def test_holding_a_harvest_stores_it():
    harvest = make_harvest()
    harvest.hold()
    assert harvest.status == "stored"

def test_the_harvest_passes_questions_on_to_its_crop():
    harvest = make_harvest(harvest_date=TODAY - timedelta(days=200))
    assert harvest.urgency() == "low"
    assert harvest.floor_price(4000) == pytest.approx(3400)
