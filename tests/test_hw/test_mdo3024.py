"""Test MDO3024"""
import pytest
from tekinstr import CommChannel

# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name
@pytest.fixture(scope="module")
def tek(request):
    addr = request.config.getoption("ipaddress")
    cc = CommChannel(addr)
    yield cc.get_instrument()
    cc.close()


def test(tek):
    assert tek.model == "MDO3024"
