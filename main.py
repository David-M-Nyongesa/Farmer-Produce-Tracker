import os
from datetime import date

from models.grain_crop import GrainCrop
from models.harvest import HarvestRecord
from models.market_price import MarketPrice
from models.perishable_crop import PerishableCrop
from services import (evaluate_offer, farmer_summary, login, regional_totals,
                      register, require_officer, sales_below_floor)
from storage import (crop_from_dict, crop_to_dict, harvest_from_dict,
                     harvest_to_dict, load_json, price_from_dict, price_to_dict,
                     save_json, user_from_dict, user_to_dict)

CROPS_FILE = os.path.join("data", "crops.json")
USERS_FILE = os.path.join("data", "users.json")
PRICES_FILE = os.path.join("data", "prices.json")
HARVESTS_FILE = os.path.join("data", "harvests.json")

users = []
crops = []
prices = []
harvests = []

def ask(question):
    return input(question + ": ").strip()

def ask_number(question):
    while True:
        try:
            return float(ask(question))
        except ValueError:
            print("Please type a number.")

def find_crop(crop_id):
    for crop in crops:
        if crop.crop_id == crop_id:
            return crop
    return None

def market_price_for(crop_id):
    for price in prices:
        if price.crop_id == crop_id:
            return price
    return None

def my_harvests(farmer):
    return [h for h in harvests if h.farmer_id == farmer.user_id]

def show_crops():
    for crop in crops:
        print(f"  {crop.crop_id}  {crop.name} (per {crop.unit})")

# farmer

def log_harvest(farmer):
    show_crops()
    crop = find_crop(ask("Crop id"))
    if crop is None:
        print("No crop with that id.")
        return
    quantity = ask_number("Quantity")
    try:
        harvest = HarvestRecord(f"H{len(harvests) + 1:04d}", farmer.user_id,
                                crop, quantity, date.today())
    except ValueError as error:
        print(error)
        return
    harvests.append(harvest)
    save_all()
    print(f"Logged {quantity} {crop.unit} of {crop.name}.")

def view_my_harvests(farmer):
    mine = my_harvests(farmer)
    if not mine:
        print("You have not logged any harvests yet.")
        return
    for harvest in mine:
        print(f"  {harvest.harvest_id}  {harvest.crop.name}  "
              f"{harvest.quantity_available} of {harvest.quantity} left  "
              f"[{harvest.status}]")
        print(f"      {harvest.crop.storage_advice()}")

def check_an_offer(farmer):
    view_my_harvests(farmer)
    harvest = find_harvest(ask("Harvest id"), farmer)
    if harvest is None:
        return
    price = market_price_for(harvest.crop.crop_id)
    if price is None:
        print("No market price has been published for that crop yet.")
        return
    if price.is_stale():
        print(f"Careful: that price is {price.days_old()} days old.")
    offer = ask_number("What is the broker offering per " + harvest.crop.unit)
    try:
        result = evaluate_offer(harvest, price.price, offer)
    except ValueError as error:
        print(error)
        return
    print(f"\n  {result['status'].upper()}")
    print(f"  {result['message']}")
    print(f"  offer {result['offer']}   floor {result['floor']:.0f}   "
          f"market {result['market']}\n")

def record_outcome(farmer):
    harvest = find_harvest(ask("Harvest id"), farmer)
    if harvest is None:
        return
    choice = ask("Did you sell or hold it? (sell/hold)")
    if choice == "hold":
        harvest.hold()
        save_all()
        print("Marked as stored.")
        return
    quantity = ask_number("How much did you sell")
    price = ask_number("At what price")
    buyer = ask("Who bought it")
    try:
        harvest.sell(quantity, price, buyer)
    except ValueError as error:
        print(error)
        return
    save_all()
    print(f"Sale recorded. {harvest.quantity_available} left.")

def find_harvest(harvest_id, farmer):
    for harvest in my_harvests(farmer):
        if harvest.harvest_id == harvest_id:
            return harvest
    print("No harvest of yours with that id.")
    return None

def farmer_menu(farmer):
    while True:
        print(f"\n-- {farmer.name} --")
        print("1 log a harvest")
        print("2 my harvests")
        print("3 check a broker's offer")
        print("4 record a sale or hold")
        print("5 log out")
        choice = ask("Choose")
        if choice == "1":
            log_harvest(farmer)
        elif choice == "2":
            view_my_harvests(farmer)
        elif choice == "3":
            check_an_offer(farmer)
        elif choice == "4":
            record_outcome(farmer)
        elif choice == "5":
            return
        else:
            print("Pick a number from the menu.")

# Officer

def add_farmer(officer):
    require_officer(officer)
    name = ask("Farmer's name")
    phone = ask("Phone number")
    password = ask("Starting password")
    try:
        register(users, f"F{len(users) + 1:03d}", name, phone, password,
                 "farmer", officer.region)
    except ValueError as error:
        print(error)
        return
    save_all()
    print(f"{name} can now log in.")

def add_crop(officer):
    require_officer(officer)
    crop_id = ask("Crop id")
    name = ask("Name")
    unit = ask("Unit")
    cost = ask_number("Cost to grow, per unit")
    kind = ask("Perishable or grain? (p/g)")
    if kind == "p":
        crop = PerishableCrop(crop_id, name, unit, cost,
                              int(ask_number("Shelf life in days")))
    else:
        crop = GrainCrop(crop_id, name, unit, cost,
                         int(ask_number("Months it can be stored")))
    crops.append(crop)
    save_all()
    print(f"Added {name}.")

def publish_price(officer):
    require_officer(officer)
    show_crops()
    crop = find_crop(ask("Crop id"))
    if crop is None:
        print("No crop with that id.")
        return
    amount = ask_number(f"Price per {crop.unit}")
    try:
        price = MarketPrice(crop.crop_id, officer.region, amount, date.today())
    except ValueError as error:
        print(error)
        return
    prices[:] = [p for p in prices if p.crop_id != crop.crop_id]
    prices.append(price)
    save_all()
    print(f"{crop.name} is now {amount} per {crop.unit}.")

def view_all_harvests(officer):
    require_officer(officer)
    if not harvests:
        print("Nobody has logged a harvest yet.")
        return
    for harvest in harvests:
        print(f"  {harvest.harvest_id}  {harvest.farmer_id}  "
              f"{harvest.crop.name}  {harvest.quantity}  [{harvest.status}]")

def show_farmer_summary(officer):
    require_officer(officer)
    for user in users:
        if user.role() == "farmer":
            print(f"  {user.user_id}  {user.name}")
    farmer_id = ask("Farmer id")
    summary = farmer_summary(harvests, farmer_id)
    print(f"  harvested  {summary['total_harvested']}")
    print(f"  sold       {summary['total_sold']}")
    print(f"  still here {summary['still_available']}")

def show_regional_totals(officer):
    require_officer(officer)
    totals = regional_totals(harvests)
    if not totals:
        print("Nothing has been harvested yet.")
        return
    for name, quantity in totals.items():
        print(f"  {name}: {quantity}")

def show_sales_below_floor(officer):
    require_officer(officer)
    market = {price.crop_id: price.price for price in prices}
    low = sales_below_floor(harvests, market)
    if not low:
        print("Every sale was at or above the floor price.")
        return
    for sale in low:
        print(f"  {sale['farmer_id']}  {sale['crop']}  sold {sale['quantity']} "
              f"at {sale['price']}, short by {sale['shortfall']:.0f} each")

def officer_menu(officer):
    while True:
        print(f"\n-- {officer.name}, {officer.region} --")
        print("1 add a farmer")
        print("2 add a crop")
        print("3 publish a market price")
        print("4 all harvests")
        print("5 a farmer's summary")
        print("6 regional totals")
        print("7 sales below the floor")
        print("8 log out")
        choice = ask("Choose")
        if choice == "1":
            add_farmer(officer)
        elif choice == "2":
            add_crop(officer)
        elif choice == "3":
            publish_price(officer)
        elif choice == "4":
            view_all_harvests(officer)
        elif choice == "5":
            show_farmer_summary(officer)
        elif choice == "6":
            show_regional_totals(officer)
        elif choice == "7":
            show_sales_below_floor(officer)
        elif choice == "8":
            return
        else:
            print("Pick a number from the menu.")

# starting up 

def save_all():
    os.makedirs("data", exist_ok=True)
    save_json(CROPS_FILE, [crop_to_dict(c) for c in crops])
    save_json(USERS_FILE, [user_to_dict(u) for u in users])
    save_json(PRICES_FILE, [price_to_dict(p) for p in prices])
    save_json(HARVESTS_FILE, [harvest_to_dict(h) for h in harvests])

def load_all():
    # crops first, harvests need them to rebuild
    crops.extend(crop_from_dict(item) for item in load_json(CROPS_FILE))
    users.extend(user_from_dict(item) for item in load_json(USERS_FILE))
    prices.extend(price_from_dict(item) for item in load_json(PRICES_FILE))
    harvests.extend(harvest_from_dict(item, crops)
                    for item in load_json(HARVESTS_FILE))
    if not crops:
        seed()

def seed():
    crops.append(GrainCrop("C001", "Maize", "bag", 2800, 12))
    crops.append(PerishableCrop("C003", "Tomato", "crate", 300, 5))
    prices.append(MarketPrice("C001", "Meru", 4000, date.today()))
    prices.append(MarketPrice("C003", "Meru", 520, date.today()))
    register(users, "O01", "Kilonzo", "0700000002", "pass1234", "officer", "Meru")
    register(users, "F001", "Njeri", "0700000001", "pass1234", "farmer", "Meru")
    save_all()

def main():
    load_all()
    print("Farmer Produce Tracker")
    while True:
        print("\n1 log in")
        print("2 exit")
        if ask("Choose") != "1":
            save_all()
            print("Bye.")
            return
        try:
            user = login(users, ask("Phone number"), ask("Password"))
        except ValueError as error:
            print(error)
            continue
        if user.role() == "officer":
            officer_menu(user)
        else:
            farmer_menu(user)

if __name__ == "__main__":
    main()