import pytest

from models.crop import Crop
from models.grain_crop import GrainCrop
from models.perishable_crop import PerishableCrop
from storage import crop_from_dict, crop_to_dict, load_json, save_json


class MysteryCrop(Crop):


    def urgency(self, days_since_harvest):
        return "low"

    def storage_advice(self):
        return "No idea."


def make_tomato():
    return PerishableCrop("C003", "Tomato", "crate", 300, shelf_life_days=5)


def make_maize():
    return GrainCrop("C001", "Maize", "bag", 2800, max_storage_months=12)


def test_a_crop_is_saved_with_its_shared_fields_and_its_type():
    data = crop_to_dict(make_maize())
    assert data["crop_id"] == "C001"
    assert data["name"] == "Maize"
    assert data["unit"] == "bag"
    assert data["cost_per_unit"] == 2800
    assert data["type"] == "grain"
    assert data["max_storage_months"] == 12


def test_a_perishable_crop_is_saved_with_its_shelf_life():
    data = crop_to_dict(make_tomato())
    assert data["type"] == "perishable"
    assert data["shelf_life_days"] == 5


def test_a_crop_is_rebuilt_as_the_right_subclass_with_its_values():
    tomato = crop_from_dict(crop_to_dict(make_tomato()))
    maize = crop_from_dict(crop_to_dict(make_maize()))
    assert isinstance(tomato, PerishableCrop)
    assert tomato.shelf_life_days == 5
    assert isinstance(maize, GrainCrop)
    assert maize.name == "Maize"
    assert maize.cost_per_unit == 2800


def test_a_rebuilt_crop_still_behaves_like_its_type():
    tomato = crop_from_dict(crop_to_dict(make_tomato()))
    maize = crop_from_dict(crop_to_dict(make_maize()))
    assert tomato.urgency(5) == "high"
    assert maize.urgency(200) == "low"


def test_a_crop_type_storage_does_not_know_cannot_be_saved():
    with pytest.raises(ValueError, match="Unknown crop type"):
        crop_to_dict(MysteryCrop("C999", "Mystery", "kg", 10))


def test_an_unknown_crop_type_is_rejected():
    with pytest.raises(ValueError, match="Unknown crop type"):
        crop_from_dict({"type": "banana", "crop_id": "X", "name": "X",
                        "unit": "kg", "cost_per_unit": 1})


def test_what_is_saved_can_be_read_back(tmp_path):
    path = tmp_path / "crops.json"
    save_json(path, [{"crop_id": "C001"}, {"crop_id": "C003"}])
    assert path.exists()
    assert load_json(path) == [{"crop_id": "C001"}, {"crop_id": "C003"}]


def test_a_missing_file_reads_as_an_empty_list(tmp_path):
    assert load_json(tmp_path / "nothing.json") == []


def test_crops_survive_a_full_round_trip(tmp_path):
    path = tmp_path / "crops.json"
    save_json(path, [crop_to_dict(make_tomato()), crop_to_dict(make_maize())])
    crops = [crop_from_dict(item) for item in load_json(path)]
    assert isinstance(crops[0], PerishableCrop)
    assert isinstance(crops[1], GrainCrop)
    assert crops[1].name == "Maize"