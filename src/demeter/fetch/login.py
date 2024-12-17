"""Login base method"""

from demeter.fetch.base import BaseRequest


class Login(BaseRequest):
    """
    Class login
    """

    def __init__(self, headers: dict = None):
        super().__init__(headers)

    def get_cookies(self, url: str, payload: dict):
        """
        Get cookies
        """
        r = self.post_method(url=url, payload=payload)
        cookies_dict = r.cookies.get_dict()

        return cookies_dict
