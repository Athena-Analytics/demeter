"""Unit tests for the CF module"""

import pytest

from demeter.fetch.cf import CF
from demeter.utils import get_config


@pytest.fixture
def cf_client():
    """Fixture to create a CF client for testing"""
    config = get_config()
    r2_url = config["R2.Config-template"]["r2_url"]
    access_key = config["R2.Config-template"]["access_key"]
    secret_key = config["R2.Config-template"]["secret_key"]
    return CF(
        url=r2_url,
        access_key=access_key,
        secret_key=secret_key,
    )


def test_get_file_from_r2(cf_client):
    """Test fetching a file from R2 storage"""

    result = cf_client.get_file_from_r2("test.log")
    assert result == b"test"
