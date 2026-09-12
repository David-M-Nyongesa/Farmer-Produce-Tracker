import pytest

from models.extension_officer import ExtensionOfficer
from models.farmer import Farmer
from models.user import User


def make_farmer():
    return Farmer("F017", "Njeri", "0700000001", "pass1234", region="Meru")


def make_officer():
    return ExtensionOfficer("O02", "Kilonzo", "0700000002", "pass1234", region="Meru")


def test_user_cannot_be_created_on_its_own():
    with pytest.raises(TypeError):
        User("U000", "Nobody", "0700000000", "pass1234")


def test_each_kind_of_user_knows_its_own_role():
    assert make_farmer().role() == "farmer"
    assert make_officer().role() == "officer"


def test_only_an_officer_may_manage_prices():
    assert make_officer().can_manage_prices() is True
    assert make_farmer().can_manage_prices() is False


def test_the_password_is_hashed_and_still_checks_out():
    farmer = make_farmer()
    assert farmer.password_hash != "pass1234"
    assert farmer.check_password("pass1234") is True
    assert farmer.check_password("wrongpass") is False


def test_the_same_password_always_gives_the_same_hash():
    assert make_farmer().password_hash == make_officer().password_hash


def test_both_kinds_of_user_can_be_treated_the_same_way():
    for user in (make_farmer(), make_officer()):
        assert isinstance(user, User)
        assert user.region == "Meru"
        assert isinstance(user.role(), str)