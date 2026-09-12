from models.crop import Crop


class PerishableCrop(Crop):
    def __init__(self, crop_id, name, unit, cost_per_unit, shelf_life_days):
        super().__init__(crop_id, name, unit, cost_per_unit)
        self.shelf_life_days = shelf_life_days

    def urgency(self, days_since_harvest):
        share = days_since_harvest / self.shelf_life_days
        if share < 0.5:
            return "low"
        if share < 0.8:
            return "medium"
        return "high"

    def storage_advice(self):
        return f"Sell within {self.shelf_life_days} days or keep it cool."