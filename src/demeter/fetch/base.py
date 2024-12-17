"""Request base method"""

from typing import Callable

import pandas as pd
import requests


class BaseRequest:
    """
    Class base requests
    """

    def __init__(self, headers=None, cookies=None):
        self._session = requests.Session()
        self._headers = headers
        self._cookies = cookies

    def _make_request_headers(self) -> dict[str, str]:

        request_headers = {
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        }

        if self._headers is not None:
            request_headers.update(self._headers)

        return request_headers

    def get_method(self, url: str, *args, **kwargs) -> requests.Response:
        """
        Get method
        """
        index = args[0] if args else 0
        params = kwargs["params"] if kwargs else {}

        try:
            print(f"start processing {index}-{params} data")

            r = self._session.get(
                url=url,
                params=params,
                headers=self._make_request_headers(),
                cookies=self._cookies,
            )

            print(f"end processing {index}-{params} data")
            return r
        except Exception as e:
            print(e)
            raise

    def post_method(self, url: str, *args, **kwargs) -> requests.Response:
        """
        Post method
        """
        index = args[0] if args else 0
        payload = kwargs["payload"] if kwargs else {}

        try:
            print(f"start processing {index}-{payload} data")

            r = self._session.post(
                url=url,
                data=payload,
                headers=self._make_request_headers(),
                cookies=self._cookies,
            )

            print(f"end processing {index}-{payload} data")
            return r
        except Exception as e:
            print(e)
            raise

    def get_df_from_reponse(
        self, process_func: Callable, r: requests.Response, data: dict
    ) -> pd.DataFrame:
        """
        Get df
        """
        result_df = process_func(r, data)
        return result_df


if __name__ == "__main__":
    pass
