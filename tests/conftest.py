"""pytest conftest"""

# pylint: disable=missing-function-docstring
def pytest_addoption(parser):
    parser.addoption("--ipaddress")
