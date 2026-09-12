from datetime import date
 
 
class MarketPrice:
    def __init__(self, crop_id, region, price, date_updated):
        check_price(price)
        self.crop_id = crop_id
        self.region = region
        self.price = price
        self.date_updated = date_updated
 
    def days_old(self, today=None):
        if today is None:
            today = date.today()
        return (today - self.date_updated).days

    def is_stale(self, stale_after_days=7, today=None):
        return self.days_old(today) > stale_after_days
 
def check_price(price):
    if price <= 0:
        raise ValueError("Price must be greater than zero")