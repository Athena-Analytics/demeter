"""Cloudflare base method"""

from demeter.fetch.base import BaseRequest


class CF(BaseRequest):
    """
    Class cf
    """

    def __init__(
        self,
        url: str,
        access_key: str,
        secret_key: str,
    ):
        super().__init__(
            headers={"X-ACCESS-KEY": access_key, "X-SECRET-KEY": secret_key}
        )
        self.url = url

    def get_file_from_r2(self, file_name: str) -> bytes:
        """
        Get template of proxy tool
        """

        r = self.get_method(url=self.url, params={"file_name": file_name})
        return r.content
