import pytest

from jml.utils import is_url


def test_is_url():
    assert is_url("https://neugebauer.cc")
    assert not is_url(str(__file__))
