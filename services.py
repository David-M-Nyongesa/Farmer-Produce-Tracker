from models.extension_officer import ExtensionOfficer
from models.farmer import Farmer


def evaluate_offer(harvest, market_price, offer, today=None):
    if offer <= 0:
        raise ValueError("Offer must be greater than zero")
    floor = harvest.floor_price(market_price)
    if offer >= market_price:
        status = "sell"
    elif offer >= floor:
        status = "negotiate"
    elif harvest.urgency(today) == "high":
        status = "sell now"
    else:
        status = "hold"
    return {
        "status": status,
        "offer": offer,
        "floor": floor,
        "market": market_price,
        "message": guidance_message(status, floor, market_price),
    }


def guidance_message(status, floor, market):
    if status == "sell":
        return "Fair offer, you may sell."
    if status == "negotiate":
        return f"Below market. Counter at {market} and do not go under {floor}."
    if status == "sell now":
        return "It will spoil. Take the best price you can get."
    return f"This is a loss. Hold out for at least {floor}."


def find_user(users, phone):
    for user in users:
        if user.phone == phone:
            return user
    return None


def register(users, user_id, name, phone, password, role, region):
    if find_user(users, phone) is not None:
        raise ValueError("That phone number is already registered")
    if role == "farmer":
        user = Farmer(user_id, name, phone, password, region)
    elif role == "officer":
        user = ExtensionOfficer(user_id, name, phone, password, region)
    else:
        raise ValueError("Unknown role")
    users.append(user)
    return user


def login(users, phone, password):
    user = find_user(users, phone)
    if user is None or not user.check_password(password):
        raise ValueError("Wrong phone number or password")
    return user


def require_officer(user):
    if not user.can_manage_prices():
        raise PermissionError("Only an extension officer can do this")
    return True


def farmer_summary(harvests, farmer_id):
    mine = [h for h in harvests if h.farmer_id == farmer_id]
    total_sold = 0
    for harvest in mine:
        for sale in harvest.sales:
            total_sold += sale["quantity"]
    return {
        "total_harvested": sum(h.quantity for h in mine),
        "total_sold": total_sold,
        "still_available": sum(h.quantity_available for h in mine),
    }


def regional_totals(harvests):
    totals = {}
    for harvest in harvests:
        name = harvest.crop.name
        totals[name] = totals.get(name, 0) + harvest.quantity
    return totals


def sales_below_floor(harvests, market_prices):
    low = []
    for harvest in harvests:
        market = market_prices.get(harvest.crop.crop_id)
        if market is None:
            continue
        floor = harvest.floor_price(market)
        for sale in harvest.sales:
            if sale["price"] < floor:
                low.append({
                    "harvest_id": harvest.harvest_id,
                    "farmer_id": harvest.farmer_id,
                    "crop": harvest.crop.name,
                    "price": sale["price"],
                    "quantity": sale["quantity"],
                    "shortfall": floor - sale["price"],
                })
    return low