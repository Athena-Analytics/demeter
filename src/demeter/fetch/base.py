"""Request base method"""

from typing import Callable

import pandas as pd
import requests


class BaseRequest:
    """
    Class base requests
    """

    def __init__(
        self,
        url: str,
        host: str | None = None,
        referrer: str | None = None,
        cookies: dict | None = None,
        headers: dict | None = None,
        user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
    ):
        self._url = url
        self._host = host
        self._referrer = referrer
        self._session = requests.Session()
        self._cookies = cookies
        self._user_agent = user_agent
        self._headers = self._make_request_headers()
        if headers is not None:
            for key, value in headers.items():
                self._headers[key] = value

    def _make_request_headers(self) -> dict[str, str]:

        request_headers = {
            "Connection": "keep-alive",
            "Host": self._host,
            "Referer": self._referrer,
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self._user_agent,
        }

        return request_headers

    def get_method(self, *args, **kwargs) -> requests.Response:
        """
        Get Method
        """
        index = args[0] if args else 0
        params = kwargs["params"] if kwargs else {}

        try:
            print(f"start processing {index}-{params} data")

            r = self._session.get(
                url=self._url,
                params=params,
                headers=self._headers,
                cookies=self._cookies,
            )

            print(f"end processing {index}-{params} data")
            return r
        except Exception as e:
            print(e)
            raise

    def post_method(self, *args, **kwargs) -> requests.Response:
        """
        Post Method
        """
        index = args[0] if args else 0
        payload = kwargs["payload"] if kwargs else {}

        try:
            print(f"start processing {index}-{payload} data")

            r = self._session.post(
                url=self._url,
                data=payload,
                headers=self._headers,
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
