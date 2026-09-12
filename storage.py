import json
import os
from datetime import date

from models.extension_officer import ExtensionOfficer
from models.farmer import Farmer
from models.grain_crop import GrainCrop
from models.harvest import HarvestRecord
from models.market_price import MarketPrice
from models.perishable_crop import PerishableCrop


def crop_to_dict(crop):
    data = {
        "crop_id": crop.crop_id,
        "name": crop.name,
        "unit": crop.unit,
        "cost_per_unit": crop.cost_per_unit,
    }
    if isinstance(crop, PerishableCrop):
        data["type"] = "perishable"
        data["shelf_life_days"] = crop.shelf_life_days
    elif isinstance(crop, GrainCrop):
        data["type"] = "grain"
        data["max_storage_months"] = crop.max_storage_months
    else:
        raise ValueError("Unknown crop type")
    return data


def crop_from_dict(data):
    if data["type"] == "perishable":
        return PerishableCrop(data["crop_id"], data["name"], data["unit"],
                              data["cost_per_unit"], data["shelf_life_days"])
    if data["type"] == "grain":
        return GrainCrop(data["crop_id"], data["name"], data["unit"],
                         data["cost_per_unit"], data["max_storage_months"])
    raise ValueError("Unknown crop type")


def save_json(path, items):
    with open(path, "w") as f:
        json.dump(items, f, indent=2)


def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)


def user_to_dict(user):
    return {
        "user_id": user.user_id,
        "name": user.name,
        "phone": user.phone,
        "password_hash": user.password_hash,
        "role": user.role(),
        "region": user.region,
    }


def user_from_dict(data):
    if data["role"] == "farmer":
        user = Farmer(data["user_id"], data["name"], data["phone"], "", data["region"])
    elif data["role"] == "officer":
        user = ExtensionOfficer(data["user_id"], data["name"], data["phone"], "",
                                data["region"])
    else:
        raise ValueError("Unknown role")
    user.password_hash = data["password_hash"]
    return user


def price_to_dict(price):
    return {
        "crop_id": price.crop_id,
        "region": price.region,
        "price": price.price,
        "date_updated": price.date_updated.isoformat(),
    }


def price_from_dict(data):
    return MarketPrice(data["crop_id"], data["region"], data["price"],
                       date.fromisoformat(data["date_updated"]))


def harvest_to_dict(harvest):
    return {
        "harvest_id": harvest.harvest_id,
        "farmer_id": harvest.farmer_id,
        "crop_id": harvest.crop.crop_id,
        "quantity": harvest.quantity,
        "harvest_date": harvest.harvest_date.isoformat(),
        "quantity_available": harvest.quantity_available,
        "status": harvest.status,
        "sales": harvest.sales,
    }


def harvest_from_dict(data, crops):
    crop = None
    for item in crops:
        if item.crop_id == data["crop_id"]:
            crop = item
    if crop is None:
        raise ValueError("Unknown crop id")
    harvest = HarvestRecord(data["harvest_id"], data["farmer_id"], crop,
                            data["quantity"], date.fromisoformat(data["harvest_date"]))
    harvest.quantity_available = data["quantity_available"]
    harvest.status = data["status"]
    harvest.sales = data["sales"]
    return harvest