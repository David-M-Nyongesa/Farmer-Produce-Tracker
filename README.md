# Farmer Produce Tracker

## Project Structure

```
Farmer-Produce-Tracker/
├── main.py                  # the CLI: menus and commands
├── services.py              # login, permissions, guidance rules
├── storage.py               # reads and writes the JSON files
├── models/                  # all the classes
│   ├── __init__.py
│   ├── crop.py
│   ├── perishable_crop.py
│   ├── grain_crop.py
│   ├── user.py
│   ├── farmer.py
│   ├── extension_officer.py
│   └── harvest.py
├── data/                    # the .json files
├── tests/
├── .github/
│   └── pull_request_template.md
├── .gitignore
├── requirements.txt
└── README.md
```
