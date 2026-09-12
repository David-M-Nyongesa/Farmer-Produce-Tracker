from models.crop import Crop


class GrainCrop(Crop):
    def __init__(self, crop_id, name, unit, cost_per_unit, max_storage_months):
        super().__init__(crop_id, name, unit, cost_per_unit)
        self.max_storage_months = max_storage_months

    def urgency(self, days_since_harvest):
        if days_since_harvest <= self.max_storage_months * 30:
            return "low"
        return "high"

    def storage_advice(self):
        return "Dry it well and store it, then sell when the price improves."