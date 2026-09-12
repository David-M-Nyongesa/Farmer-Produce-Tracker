from abc import ABC, abstractmethod


class Crop(ABC):
    def __init__(self, crop_id, name, unit, cost_per_unit):
        self.crop_id = crop_id
        self.name = name
        self.unit = unit
        self.cost_per_unit = cost_per_unit

    def break_even(self, margin=0.10):
        return self.cost_per_unit * (1 + margin)

    def floor_price(self, market_price, margin=0.10, floor_pct=0.85):
        return max(self.break_even(margin), market_price * floor_pct)

    @abstractmethod
    def urgency(self, days_since_harvest):
        pass

    @abstractmethod
    def storage_advice(self):
        pass