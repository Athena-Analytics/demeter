"""Unit tests for mailbox module"""

import pandas as pd

from demeter.fetch.mailbox import AnytimeMailbox, IPostalMailbox


def test_get_anytime_mailbox_list():
    """Test fetching mailbox list from Anytime Mailbox"""
    mailbox = AnytimeMailbox()
    result = mailbox.get_anytime_mailbox_list()

    assert isinstance(result, list)
    assert len(result) > 0

    for item in result:
        assert "title" in item
        assert "price" in item
        assert "address" in item
        assert "detail_domain" in item
        assert isinstance(item["title"], str)
        assert isinstance(item["price"], str)
        assert isinstance(item["address"], str)
        assert isinstance(item["detail_domain"], str)
        assert item["detail_domain"].startswith("https://www.anytimemailbox.com")


def test_get_anytime_mailbox_detail():
    """Test fetching mailbox details from Anytime Mailbox"""
    mailbox = AnytimeMailbox()
    result = mailbox.get_anytime_mailbox_detail(
        "https://www.anytimemailbox.com/s/ashland-1467-siskiyou-blvd"
    )

    assert isinstance(result, dict)
    assert "functions" in result
    assert "carriers" in result
    assert isinstance(result["functions"], dict)
    assert isinstance(result["carriers"], list)

    for status in result["functions"].values():
        assert status in ["on", "off"]


def test_parse_ipostal_mailbox_list():
    """Test parsing mailbox list from iPostal"""
    mailbox = IPostalMailbox()

    # Create sample DataFrame
    sample_data = {
        "display": [
            '<article class="mail-center-card" store-id="123" store-tooltip="Test Address">'
            '<div class="shipping-status">Active</div>'
            '<p class="store-plan-desktop">Desktop Plan</p>'
            '<p class="store-plan-mobile">Mobile Plan</p>'
            "</article>"
        ]
    }
    df = pd.DataFrame(sample_data)

    result = mailbox.parse_ipostal_mailbox_list(df)

    assert isinstance(result, dict)
    assert "store_id" in result
    assert "store_address" in result
    assert "shipping_status" in result
    assert "store_plan_desktop" in result
    assert "store_plan_mobile" in result

    assert result["store_id"] == ["123"]
    assert result["store_address"] == ["Test Address"]
    assert result["shipping_status"] == ["Active"]
    assert result["store_plan_desktop"] == ["Desktop Plan"]
    assert result["store_plan_mobile"] == ["Mobile Plan"]
