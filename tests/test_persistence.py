from datetime import date, timedelta

import pytest

from models.extension_officer import ExtensionOfficer
from models.farmer import Farmer
from models.grain_crop import GrainCrop
from models.harvest import HarvestRecord
from models.market_price import MarketPrice
from storage import (harvest_from_dict, harvest_to_dict, price_from_dict,
                     price_to_dict, user_from_dict, user_to_dict)
TODAY = date.today()

def make_farmer():
    return Farmer("F017", "Njeri", "0700000001", "pass1234", "Meru")

def make_officer():
    return ExtensionOfficer("O02", "Kilonzo", "0700000002", "pass1234", "Meru")

def make_maize():
    return GrainCrop("C001", "Maize", "bag", 2800, max_storage_months=12)

def make_harvest():
    harvest = HarvestRecord("H01", "F017", make_maize(), 20, TODAY)
    harvest.sell(12, price=3600, buyer="Broker Ali")
    return harvest

def test_a_user_is_saved_with_their_role_and_region_but_never_the_password():
    data = user_to_dict(make_farmer())
    assert data["role"] == "farmer"
    assert data["region"] == "Meru"
    assert "pass1234" not in str(data)
    assert data["password_hash"] != ""

def test_a_user_is_rebuilt_as_the_right_kind_and_can_still_log_in():
    farmer = user_from_dict(user_to_dict(make_farmer()))
    officer = user_from_dict(user_to_dict(make_officer()))
    assert isinstance(farmer, Farmer)
    assert isinstance(officer, ExtensionOfficer)
    assert farmer.name == "Njeri"
    assert farmer.check_password("pass1234") is True
    assert farmer.check_password("wrongpass") is False

def test_an_unknown_role_is_rejected():
    with pytest.raises(ValueError, match="Unknown role"):
        user_from_dict({"user_id": "X", "name": "X", "phone": "07", "role": "broker",
                        "region": "Meru", "password_hash": "abc"})

def test_a_price_is_saved_as_text_and_rebuilt_with_its_values():
    data = price_to_dict(MarketPrice("C001", "Meru", 4000, TODAY))
    assert data["date_updated"] == TODAY.isoformat()
    price = price_from_dict(data)
    assert price.price == 4000
    assert price.date_updated == TODAY

def test_a_rebuilt_price_still_knows_if_it_is_stale():
    old = MarketPrice("C001", "Meru", 4000, TODAY - timedelta(days=8))
    assert price_from_dict(price_to_dict(old)).is_stale() is True

def test_a_harvest_is_saved_with_the_crop_id_not_the_crop():
    assert harvest_to_dict(make_harvest())["crop_id"] == "C001"

def test_a_rebuilt_harvest_keeps_its_state_and_its_sales():
    harvest = harvest_from_dict(harvest_to_dict(make_harvest()), [make_maize()])
    assert harvest.quantity == 20
    assert harvest.quantity_available == 8
    assert harvest.status == "available"
    assert harvest.sales[0]["price"] == 3600

def test_a_rebuilt_harvest_still_gives_a_floor_price():
    harvest = harvest_from_dict(harvest_to_dict(make_harvest()), [make_maize()])
    assert harvest.floor_price(4000) == pytest.approx(3400)

def test_a_harvest_with_an_unknown_crop_is_rejected():
    with pytest.raises(ValueError, match="Unknown crop id"):
        harvest_from_dict(harvest_to_dict(make_harvest()), [])
