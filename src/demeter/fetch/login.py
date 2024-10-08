"""Login base method"""

from demeter.fetch.base import BaseRequest


class Login(BaseRequest):
    """
    Class login
    """

    def __init__(self, url: str, host: str, referrer: str):
        super().__init__(url, host, referrer)

    def get_cookies(self, payload: dict):
        """
        Get cookies
        """
        r = self.post_method(payload=payload)
        cookies_dict = r.cookies.get_dict()

        return cookies_dict
