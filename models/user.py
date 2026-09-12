import hashlib
from abc import ABC, abstractmethod


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


class User(ABC):
    def __init__(self, user_id, name, phone, password):
        self.user_id = user_id
        self.name = name
        self.phone = phone
        self.password_hash = hash_password(password)

    def check_password(self, password):
        return hash_password(password) == self.password_hash

    @abstractmethod
    def role(self):
        pass

    @abstractmethod
    def can_manage_prices(self):
        pass