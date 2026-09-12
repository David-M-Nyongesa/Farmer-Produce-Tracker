# Farmer Produce Tracker

A command-line tool that helps smallholder farmers record their harvests and decide
whether a broker's offer is worth taking.

A farmer logs what they harvested and what it cost to grow. An extension officer keeps
the market price for each crop up to date. When a broker makes an offer, the farmer
enters it and the system says whether to sell, negotiate, or hold.

## The problem

Most smallholders keep no record of what a crop cost to grow, and they rarely know the
day's market price. The broker knows both. The first offer at the farm gate usually gets
accepted, and it is often below what the crop cost to produce.

## How the advice works

For every harvest the system works out a floor price, which is the lowest price the
farmer should accept:

```
break-even = cost to grow per unit + a 10% margin
floor      = the higher of break-even and 85% of the market price
```

An offer is then judged against the floor and the market price:

| Offer | Advice |
|---|---|
| At or above the market price | Sell |
| Between the floor and the market price | Negotiate |
| Below the floor, crop can wait | Hold |
| Below the floor, crop about to spoil | Sell now |

The last row is why crops are split into two types. A grain crop can be dried and
stored, so a low offer becomes advice to hold. A perishable crop spoils, so as it
approaches the end of its shelf life the same low offer becomes advice to sell now and
limit the loss.

## Setup

You need Python installed

```bash
git clone https://github.com/David-M-Nyongesa/Farmer-Produce-Tracker.git
cd Farmer-Produce-Tracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running it

```bash
python main.py
```

Two accounts are created the first time you run it:

| Role | Phone | Password |
|---|---|---|
| Extension officer | 0700000002 | pass1234 |
| Farmer | 0700000001 | pass1234 |

### As a farmer

Log in, then log a harvest by choosing a crop, the quantity, and what it cost you per
unit. Option 2 lists your harvests with storage advice for each. When a broker makes an
offer, option 3 asks which harvest and what they offered, then tells you what to do and
shows the numbers behind it. Option 4 records what actually happened, either a sale or a
decision to hold.

You only ever see your own records.

### As an extension officer

Log in to add farmers, add crops to the catalogue, and publish market prices for your
region. Options 5 to 7 are the reports: one farmer's summary, total production per crop
across the region, and every sale that went below the floor price, with the shortfall on
each.

Officers cannot log harvests, and farmers cannot publish prices. Either attempt is
refused.

## Running the tests

```bash
python -m pytest tests/
```

With coverage:

```bash
python -m pytest tests/ --cov=models --cov=services --cov=storage
```

Coverage is measured on the three tested layers. `main.py` is the user interface and is
checked by hand, not by tests, which is why it is not included.

## Project structure

```
Farmer-Produce-Tracker/
├── main.py              the menus, and nothing else
├── services.py          login, permissions, guidance rules, reports
├── storage.py           reads and writes the JSON files
├── models/              the classes
│   ├── crop.py          abstract Crop
│   ├── perishable_crop.py
│   ├── grain_crop.py
│   ├── user.py          abstract User
│   ├── farmer.py
│   ├── extension_officer.py
│   ├── harvest.py
│   └── market_price.py
├── data/                the saved .json files
├── tests/
├── .github/
│   └── pull_request_template.md
├── requirements.txt
└── README.md
```

All the rules live in `models/` and `services.py`. `main.py` only reads input, calls
those functions, and prints what comes back. That separation is what makes the rules
testable without a user sitting at a keyboard.

## The classes

```
        Crop (abstract)                     User (abstract)
       /              \                    /              \
PerishableCrop    GrainCrop           Farmer        ExtensionOfficer
```

`Crop` holds what every crop has: an id, a name, a unit, and what it costs to grow. It
declares `urgency()` and `storage_advice()` but does not implement them, because the
answer depends on whether the crop spoils or stores. Each subclass overrides both.

Nothing outside the crop classes ever checks which type it is holding. `HarvestRecord`
asks its crop for the answer, and the guidance engine asks the harvest. That is the point
of the hierarchy: the rule that differs between a tomato and a bag of maize lives in one
place.

`User` works the same way. `Farmer` and `ExtensionOfficer` override `role()` and
`can_manage_prices()`, and the permission check just asks the user rather than comparing
strings.

Supporting classes: `HarvestRecord` is one logged harvest and tracks what has been sold
from it. `MarketPrice` is a published price with the date it was set, so an old price can
be flagged as stale.

## Storing data

Everything is kept in JSON files under `data/`. Objects cannot go into JSON directly, so
each one is converted to a dictionary on the way out and rebuilt on the way in. Crops
carry a `type` field so the right subclass comes back. Harvests store only the crop's id,
so crops are always loaded first.

Passwords are never stored. Only a SHA-256 hash of the password is saved, and login
compares hashes.

To start from scratch, delete the `data/` folder and run the program again.

## Built by

- <!-- David Nyongesa --> 
- <!-- Carlos Muchemi -->
- <!-- Keith Gachuche -->

Scrum master: <!-- David Nyongesa -->

Board: <!-- https://trello.com/invite/b/6aa14485f61483144fa3efa3/ATTIbb67cd9a7e1747080f797c704af5ae88F1BD57DF/farmer-produce-tracker -->
