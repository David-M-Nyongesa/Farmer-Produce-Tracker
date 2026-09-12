from datetime import date
 
 
class HarvestRecord:
    def __init__(self, harvest_id, farmer_id, crop, quantity, harvest_date):
        check_quantity(quantity)
        check_date(harvest_date)
        self.harvest_id = harvest_id
        self.farmer_id = farmer_id
        self.crop = crop
        self.quantity = quantity
        self.harvest_date = harvest_date
        self.quantity_available = quantity
        self.status = "available"
        self.sales = []
 
    def days_since_harvest(self, today=None):
        if today is None:
            today = date.today()
        return (today - self.harvest_date).days

    def urgency(self, today=None):
        return self.crop.urgency(self.days_since_harvest(today))

    def floor_price(self, market_price):
        return self.crop.floor_price(market_price)

    def sell(self, quantity, price, buyer):
        if quantity > self.quantity_available:
            raise ValueError("Cannot sell more than the quantity available")
        self.quantity_available -= quantity
        self.sales.append({"quantity": quantity, "price": price, "buyer": buyer})
        if self.quantity_available == 0:
            self.status = "sold"

    def hold(self):
        self.status = "stored"

def check_quantity(quantity):
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero")
    
def check_date(harvest_date):
    if harvest_date > date.today():
        raise ValueError("Harvest date cannot be in the future")