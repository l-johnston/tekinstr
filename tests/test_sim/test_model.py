"""Test Model"""
import os
import pytest
from tekinstr import CommChannel

# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name
@pytest.fixture(scope="module")
def tek(request):
    path = os.path.dirname(os.path.abspath(__file__))
    os.environ["PYVISA_LIBRARY"] = path + r"\sim_hw.yml@sim"
    address = request.config.getoption("ipaddress")
    cc = CommChannel(address)
    yield cc.get_instrument()
    cc.close()


def test_model(tek):
    assert tek.model == "MDO3024"
