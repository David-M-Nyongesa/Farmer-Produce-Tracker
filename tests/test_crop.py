import pytest

from models.crop import Crop
from models.grain_crop import GrainCrop
from models.perishable_crop import PerishableCrop


def make_tomato():
    return PerishableCrop("C003", "Tomato", "crate", 300, shelf_life_days=5)


def make_maize():
    return GrainCrop("C001", "Maize", "bag", 2800, max_storage_months=12)


def test_crop_cannot_be_created_on_its_own():
    with pytest.raises(TypeError):
        Crop("C000", "Nothing", "kg", 100)


def test_break_even_adds_the_margin():
    maize = make_maize()
    assert maize.break_even() == pytest.approx(3080)


def test_floor_price_uses_break_even_when_it_is_higher():
    maize = make_maize()
    assert maize.floor_price(3000) == pytest.approx(3080)


def test_floor_price_uses_the_market_price_when_it_is_higher():
    maize = make_maize()
    assert maize.floor_price(4000) == pytest.approx(3400)


def test_tomato_is_not_urgent_when_fresh():
    assert make_tomato().urgency(0) == "low"


def test_tomato_gets_more_urgent_as_it_ages():
    assert make_tomato().urgency(3) == "medium"


def test_tomato_is_urgent_near_its_shelf_life():
    assert make_tomato().urgency(5) == "high"


def test_maize_is_not_urgent_while_it_can_be_stored():
    assert make_maize().urgency(200) == "low"


def test_maize_is_urgent_once_storage_runs_out():
    assert make_maize().urgency(400) == "high"


def test_tomato_advises_selling():
    assert "sell" in make_tomato().storage_advice().lower()


def test_maize_advises_drying():
    assert "dry" in make_maize().storage_advice().lower()


def test_both_crops_work_the_same_way():
    for crop in (make_tomato(), make_maize()):
        assert crop.floor_price(5000) > 0
        assert crop.urgency(1) in ("low", "medium", "high")
        assert isinstance(crop.storage_advice(), str)
