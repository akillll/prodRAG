"""Smoke test for the backend test configuration."""

import pytest


@pytest.mark.unit
def test_pytest_discovers_unit_tests() -> None:
    """Confirm that pytest discovers and executes typed unit tests."""
    assert True
