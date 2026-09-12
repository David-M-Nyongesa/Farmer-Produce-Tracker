from models.user import User


class Farmer(User):
    def __init__(self, user_id, name, phone, password, region):
        super().__init__(user_id, name, phone, password)
        self.region = region

    def role(self):
        return "farmer"

    def can_manage_prices(self):
        return False