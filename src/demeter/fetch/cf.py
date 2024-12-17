"""Cloudflare base method"""

from demeter.fetch.base import BaseRequest


class CF(BaseRequest):
    """
    Class cf
    """

    def __init__(
        self,
        access_key: str,
        secret_key: str,
    ):
        headers = {"X-ACCESS-KEY": access_key, "X-SECRET-KEY": secret_key}
        super().__init__(headers=headers)

    def get_file_from_r2(self, url: str, file_name: str) -> bytes:
        """
        Get template of proxy tool
        """

        r = self.get_method(url=url, params={"file_name": file_name})
        return r.content
