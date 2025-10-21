"""Log in to a server and retrieve cookies"""

from demeter.fetch.base import BaseRequest


class Login(BaseRequest):
    """
    Class to handle login and cookie retrieval for a given URL
    """

    def __init__(self, url: str, headers: dict = None):
        super().__init__(headers)
        self.url = url

    def get_cookies(self, payload: dict):
        """
        Get cookies from the server after posting the payload

        Args:
            payload (dict): Data to be sent in the POST request
        Returns:
            dict: Dictionary of cookies received from the server
        """
        r = self.post_method(url=self.url, payload=payload)
        cookies_dict = r.cookies.get_dict()

        return cookies_dict
