"""Login base method"""

from demeter.fetch.base import BaseRequest


class Login(BaseRequest):
    """
    Class login
    """

    def __init__(self, url: str, headers: dict = None):
        super().__init__(headers)
        self.url = url

    def get_cookies(self, payload: dict):
        """
        Get cookies
        """
        r = self.post_method(url=self.url, payload=payload)
        cookies_dict = r.cookies.get_dict()

        return cookies_dict
