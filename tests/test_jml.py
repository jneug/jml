import pytest

from jml.jml import __version__


def test_version():
    assert __version__ == "0.4.3"
