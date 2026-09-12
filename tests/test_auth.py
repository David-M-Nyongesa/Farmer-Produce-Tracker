import pytest

from models.extension_officer import ExtensionOfficer
from models.farmer import Farmer
from services import find_user, login, register, require_officer

def make_users():
    users = []
    register(users, "F017", "Njeri", "0700000001", "pass1234", "farmer", "Meru")
    register(users, "O02", "Kilonzo", "0700000002", "pass1234", "officer", "Meru")
    return users

def test_registering_creates_the_right_kind_of_user_and_adds_them():
    users = make_users()
    assert isinstance(users[0], Farmer)
    assert isinstance(users[1], ExtensionOfficer)
    assert len(users) == 2

def test_the_password_is_not_kept_as_plain_text():
    users = make_users()
    assert users[0].password_hash != "pass1234"

def test_the_same_phone_number_cannot_be_used_twice():
    users = make_users()
    with pytest.raises(ValueError, match="That phone number is already registered"):
        register(users, "F018", "Kamau", "0700000001", "pass1234", "farmer", "Meru")

def test_an_unknown_role_is_rejected():
    with pytest.raises(ValueError, match="Unknown role"):
        register([], "X01", "Nobody", "0700000009", "pass1234", "broker", "Meru")

def test_a_user_can_be_looked_up_by_phone_number():
    users = make_users()
    assert find_user(users, "0700000001").name == "Njeri"
    assert find_user(users, "0700009999") is None

def test_login_with_the_right_details_returns_the_user():
    assert login(make_users(), "0700000001", "pass1234").name == "Njeri"

def test_login_is_refused_for_a_wrong_password_or_unknown_number():
    users = make_users()
    with pytest.raises(ValueError, match="Wrong phone number or password"):
        login(users, "0700000001", "wrongpass")
    with pytest.raises(ValueError, match="Wrong phone number or password"):
        login(users, "0700009999", "pass1234")

def test_an_officer_is_allowed_through_and_a_farmer_is_blocked():
    users = make_users()
    assert require_officer(users[1]) is True
    with pytest.raises(PermissionError, match="Only an extension officer can do this"):
        require_officer(users[0])
