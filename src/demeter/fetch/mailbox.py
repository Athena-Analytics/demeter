"""Mailbox base method"""

import pandas as pd
from lxml import html

from demeter.fetch.base import BaseRequest


class AnytimeMailbox(BaseRequest):
    """
    Class Anytime Mailbox
    """

    def get_anytime_mailbox_list(
        self, country: str = "usa", state: str = "california"
    ) -> list:
        """
        Fetch mailbox list from Anytime Mailbox

        Args:
            country: Country code (default 'usa')
            state: State code (default 'california')

        Returns:
            List of dictionaries containing mailbox information
        """
        base_url = "https://www.anytimemailbox.com"
        url = f"{base_url}/l/{country}/{state}"

        r = self.get_method(url=url)
        tree = html.fromstring(r.content)
        items = tree.xpath("//div[@class='theme-location-item']")

        result = []
        for item in items:
            title = item.xpath(".//h3[@class='t-title']/text()")[0]
            price = item.xpath(".//div[@class='t-price']//b/text()")[0]
            address = " ".join(item.xpath(".//div[@class='t-addr']/text()"))
            detail_domain = base_url + item.xpath(".//a/@href")[0]
            result.append(
                {
                    "title": title,
                    "price": price,
                    "address": address,
                    "detail_domain": detail_domain,
                }
            )
        return result

    def get_anytime_mailbox_detail(self, detail_domain: str) -> dict:
        """
        Fetch mailbox details from Anytime Mailbox

        Args:
            detail_domain: URL of the mailbox detail page

        Returns:
            Dictionary containing mailbox details
        """
        r = self.get_method(url=detail_domain)
        tree = html.fromstring(r.content)

        # Get functions
        function_items = tree.xpath(
            "//div[@class='t-sec1']//div[@class='t-feat']//td/div[contains(@class, 't-')]"
        )
        functions = {}
        for item in function_items:
            status = "on" if item.get("class") == "t-on" else "off"
            name = item.xpath(".//div[2]/text()")[0]
            functions[name] = status

        # Get shipping carriers
        carrier_items = tree.xpath("//div[@class='t-sec2']//div[@class='t-ship']/img")
        carriers = []
        for img in carrier_items:
            carrier = img.get("title").replace("Ship with ", "")
            carriers.append(carrier)
        carriers.sort()
        return {
            "functions": functions,
            "carriers": carriers,
        }


class IPostalMailbox(BaseRequest):
    """
    Class IPostal Mailbox
    """

    def parse_ipostal_mailbox_list(self, df: pd.DataFrame) -> dict:
        """
        Parse iPostal mailbox list

        Args:
            df: DataFrame containing mailbox list, https://ipostal1.com/locations_ajax.php?action=get_mail_centers&state=AK&city=&country_id=223

        Returns:
            Dictionary containing parsed mailbox details
        """

        display = df["display"].values[0]
        tree = html.fromstring(display)

        # Extract specific elements
        store_id = [
            dict(item.attrib)["store-id"]
            for item in tree.xpath("//article[@class='mail-center-card']")
        ]
        store_address = [
            dict(item.attrib)["store-tooltip"]
            for item in tree.xpath("//article[@class='mail-center-card']")
        ]
        shipping_status = [
            item.text_content().strip()
            for item in tree.xpath("//div[contains(@class, 'shipping-status')]")
        ]
        store_plan_desktop = [
            item.text_content().strip()
            for item in tree.xpath("//p[contains(@class, 'store-plan-desktop')]")
        ]
        store_plan_mobile = [
            item.text_content().strip()
            for item in tree.xpath("//p[contains(@class, 'store-plan-mobile')]")
        ]

        result = {
            "store_id": store_id,
            "store_address": store_address,
            "shipping_status": shipping_status,
            "store_plan_desktop": store_plan_desktop,
            "store_plan_mobile": store_plan_mobile,
        }

        return result
