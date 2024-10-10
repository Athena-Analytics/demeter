"""Proxy config base method"""

import re
from ast import literal_eval

from demeter.fetch.base import BaseRequest
from demeter.utils import decode_base64_str


class ProxyConfig(BaseRequest):
    """
    Class of transfer all proxies to dict
    """

    def __init__(self, sub_url: str, custom_link: str):
        super().__init__(url=decode_base64_str(sub_url))
        self.custom_link = custom_link

    @staticmethod
    def _decode_sub_link(proxy_link: str) -> tuple[str, str, str]:
        proxy_protocol, proxy_content = proxy_link.split("://")

        if proxy_protocol == "ss":
            proxy_configuration_base64, proxy_name = proxy_content.split("#")
        else:
            proxy_configuration_base64 = proxy_content
            proxy_name = ""

        proxy_configuration = decode_base64_str(proxy_configuration_base64)

        return proxy_protocol, proxy_configuration, proxy_name

    @staticmethod
    def _get_proxy_component(
        tool_type: str, proxy_protocol: str, proxy_configuration: str, proxy_name: str
    ) -> dict:

        if proxy_protocol == "ss":
            components = proxy_configuration.split("@")
            cipher, password = components[0].split(":")
            address, port = components[1].split(":")

            proxy_component = {
                "server": address,
                "password": password,
            }

            if tool_type == "clash":
                proxy_component.update(
                    {
                        "type": "ss",
                        "name": proxy_name,
                        "port": int(port),
                        "cipher": cipher,
                        "udp": True,
                    }
                )
            elif re.search("singbox", tool_type):
                proxy_component.update(
                    {
                        "type": "shadowsocks",
                        "tag": proxy_name,
                        "server_port": int(port),
                        "method": cipher,
                    }
                )

            return proxy_component

        if proxy_protocol == "vmess":
            proxy_configuration_dict = literal_eval(proxy_configuration)
            proxy_name = proxy_configuration_dict["ps"]
            uid = proxy_configuration_dict["id"]
            address = proxy_configuration_dict["add"]
            port = proxy_configuration_dict["port"]
            aid = proxy_configuration_dict["aid"]
            cipher = (
                proxy_configuration_dict["scy"]
                if "scy" in proxy_configuration_dict
                else "auto"
            )
            tls = (
                False
                if "tls" in proxy_configuration_dict
                and proxy_configuration_dict["tls"] == "none"
                else True
            )
            network = (
                proxy_configuration_dict["net"]
                if "net" in proxy_configuration_dict
                else "tcp"
            )
            sni = (
                proxy_configuration_dict["sni"]
                if "sni" in proxy_configuration_dict
                and proxy_configuration_dict["sni"] != ""
                else ""
            )
            ws_option = (
                {"path": proxy_configuration_dict["path"]} if network == "ws" else {}
            )

            proxy_component = {
                "type": "vmess",
                "server": address,
                "uuid": uid,
            }

            if tool_type == "clash":
                other_proxy_component = {
                    "name": proxy_name,
                    "port": int(port),
                    "alterId": int(aid),
                    "cipher": cipher,
                    "udp": True,
                    "tls": tls,
                    "skip-cert-verify": False,
                    "network": network,
                }
                if tls and sni != "":
                    other_proxy_component["servername"] = sni
                if network == "ws":
                    other_proxy_component["ws-opts"] = ws_option

            elif re.search("singbox", tool_type):
                other_proxy_component = {
                    "tag": proxy_name if proxy_name != "Vmess-ws" else "Vmess_ws",
                    "server_port": int(port),
                    "security": cipher,
                    "global_padding": True,
                    "packet_encoding": "xudp",
                }
                if tls and sni != "":
                    other_proxy_component["tls"] = {
                        "enabled": True,
                        "server_name": sni,
                        "insecure": False,
                        "min_version": "1.2",
                        "max_version": "1.3",
                    }
                if network == "ws":
                    other_proxy_component["transport"] = {"type": "ws"}
                    other_proxy_component["transport"].update(ws_option)

            proxy_component.update(other_proxy_component)
            return proxy_component

        raise ValueError(f"Can't recognize the proxy_protocol {proxy_protocol}")

    def get_proxies(self, tool_type: str) -> list:
        """
        Get proxies
        """
        try:
            proxies = []

            r = self.get_method()
            proxy_links = decode_base64_str(r.text).split("\n")

            custom_link_decoded = (
                None
                if self.custom_link is None
                else decode_base64_str(self.custom_link).split("|")
            )

            if custom_link_decoded is not None:
                proxy_links.extend(custom_link_decoded)

            for proxy_link in proxy_links:
                proxy_protocol, proxy_configuration, proxy_name = self._decode_sub_link(
                    proxy_link
                )
                proxy = self._get_proxy_component(
                    tool_type, proxy_protocol, proxy_configuration, proxy_name
                )
                proxies.append(proxy)

            return proxies

        except TimeoutError as e:
            print(e)
            raise
