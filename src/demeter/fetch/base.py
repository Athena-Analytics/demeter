"""Base request class for handling HTTP requests"""

from typing import Callable
from urllib.parse import urlparse

import pandas as pd
import requests


class BaseRequest:
    """
    Class to handle basic HTTP requests with GET and POST methods
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
        Send a GET request to the specified URL

        Args:
            url (str): URL to send the GET request to
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments, including 'params'
        Returns:
            requests.Response: The response object from the GET request
        Raises:
            Exception: If an error occurs during the request
        """
        base_url = urlparse(url).netloc
        path = urlparse(url).path.strip("/")
        index = args[0] if args else 0
        params = kwargs["params"] if kwargs else None

        try:
            print("==========\nstart processing GET request")

            print(
                f"index: {index}, base_url: {base_url}, path: {path}, params: {params}"
            )

            r = self._session.get(
                url=url,
                params=params,
                headers=self._make_request_headers(),
                cookies=self._cookies,
            )

            print("end processing GET request\n==========")
            return r
        except Exception as e:
            print(e)
            raise

    def post_method(self, url: str, *args, **kwargs) -> requests.Response:
        """
        Send a POST request to the specified URL

        Args:
            url (str): URL to send the POST request to
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments, including 'payload'
        Returns:
            requests.Response: The response object from the POST request
        Raises:
            Exception: If an error occurs during the request
        """
        base_url = urlparse(url).netloc
        path = urlparse(url).path.strip("/")
        index = args[0] if args else 0
        payload = kwargs["payload"] if kwargs else None

        try:
            print("==========\nstart processing POST request")

            print(
                f"index: {index}, base_url: {base_url}, path: {path}, payload: {payload}"
            )

            r = self._session.post(
                url=url,
                data=payload,
                headers=self._make_request_headers(),
                cookies=self._cookies,
            )

            print("end processing POST request\n==========")
            return r
        except Exception as e:
            print(e)
            raise

    def get_df_from_response(
        self, process_func: Callable, r: requests.Response, data: dict
    ) -> pd.DataFrame:
        """
        Convert response to DataFrame using the provided processing function

        Args:
            process_func (Callable): Function to process the response and convert it to a DataFrame
            r (requests.Response): The response object from the request
            data (dict): Additional data required for processing the response
        Returns:
            pd.DataFrame: The processed DataFrame
        """
        result_df = process_func(r, data)
        return result_df
