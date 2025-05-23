"""Proxy config base method"""

import re
from ast import literal_eval

from demeter.fetch.base import BaseRequest
from demeter.utils import decode_base64_str


class ProxyConfig(BaseRequest):
    """
    Class proxy config
    """

    def __init__(self, sub_url: str, custom_link: str):
        super().__init__()
        self.sub_url = sub_url
        self.custom_link = custom_link

    @staticmethod
    def _decode_sub_link(proxy_link: str) -> tuple[str, str, str]:
        proxy_protocol, proxy_content = proxy_link.split("://")

        if proxy_protocol == "ss":
            return (
                proxy_protocol,
                decode_base64_str(proxy_content.split("#")[0]),
                proxy_content.split("#")[1],
            )

        if proxy_protocol in ["vmess", "vless"]:
            return proxy_protocol, decode_base64_str(proxy_content.split("#")[0]), ""

        raise ValueError(
            f"proxy_protocol must be ss, vmess, vless. but got {proxy_protocol}"
        )

    @staticmethod
    def _get_tool_component_by_ss(
        tool_type: str,
        proxy_name: str,
        password: str,
        address: str,
        port: int,
        cipher: str,
    ) -> dict:

        if tool_type == "clash":
            return {
                "name": proxy_name,
                "type": "ss",
                "server": address,
                "port": int(port),
                "cipher": cipher,
                "password": password,
                "udp": True,
            }

        if re.search("singbox", tool_type):
            return {
                "type": "shadowsocks",
                "tag": proxy_name,
                "server": address,
                "server_port": int(port),
                "method": cipher,
                "password": password,
            }

    @staticmethod
    def _get_tool_component_by_vmess(
        tool_type: str,
        proxy_name: str,
        uuid: str,
        address: str,
        port: int,
        aid: int,
        cipher: str,
        network: str,
        tls: bool,
        **kwargs,
    ) -> dict:

        if tool_type == "clash":
            proxy_component = {
                "name": proxy_name,
                "type": "vmess",
                "server": address,
                "port": port,
                "uuid": uuid,
                "alterId": aid,
                "cipher": cipher,
                "udp": True,
                "skip-cert-verify": False,
                "network": network,
            }
            if tls:
                proxy_component["tls"] = tls
                if "sni" in kwargs and kwargs["sni"] != "":
                    proxy_component["server_name"] = kwargs["sni"]

            if network == "ws":
                proxy_component["ws-opts"] = kwargs["ws_option"]

            return proxy_component

        if re.search("singbox", tool_type):
            proxy_component = {
                "type": "vmess",
                "tag": proxy_name,
                "server": address,
                "server_port": port,
                "uuid": uuid,
                "security": cipher,
                "alter_id": aid,
                "global_padding": True,
                "network": "tcp",
                "packet_encoding": "xudp",
            }

            if tls:
                proxy_component["tls"] = {
                    "enabled": True,
                    "insecure": False,
                    "alpn": kwargs["alpn"],
                    "min_version": "1.2",
                    "max_version": "1.3",
                }
                if "sni" in kwargs and kwargs["sni"] != "":
                    proxy_component["tls"]["server_name"] = kwargs["sni"]

            if network == "ws":
                transport = {"type": "ws"}
                transport.update(kwargs["ws_option"])
                proxy_component["transport"] = transport

            return proxy_component

    @staticmethod
    def _get_tool_component_by_vless(
        tool_type: str,
        proxy_name: str,
        uuid: str,
        address: str,
        port: int,
        flow: str,
        network: str,
        tls: bool,
        **kwargs,
    ) -> dict:

        if tool_type == "clash":

            return {}

        if re.search("singbox", tool_type):
            proxy_component = {
                "type": "vless",
                "tag": proxy_name,
                "server": address,
                "server_port": port,
                "uuid": uuid,
                "flow": flow,
                "network": network,
                "packet_encoding": "xudp",
            }

            if tls:
                proxy_component["tls"] = {
                    "enabled": True,
                    "insecure": False,
                    "min_version": "1.2",
                    "max_version": "1.3",
                }
                if "sni" in kwargs and kwargs["sni"] != "":
                    proxy_component["tls"]["server_name"] = kwargs["sni"]

            if network == "ws":
                proxy_component["transport"] = {"type": "ws"}
                proxy_component["transport"].update(kwargs["ws_option"])

            return proxy_component

    def get_proxy_component(
        self,
        tool_type: str,
        proxy_protocol: str,
        proxy_configuration: str,
        proxy_name: str,
    ) -> dict:
        """
        Get proxy component
        """

        if proxy_protocol == "ss":
            components = proxy_configuration.split("@")
            cipher, password = components[0].split(":")
            address, port = components[1].split(":")

            proxy_component = self._get_tool_component_by_ss(
                tool_type, proxy_name, password, address, int(port), cipher
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
            network = (
                proxy_configuration_dict["net"]
                if "net" in proxy_configuration_dict
                else "tcp"
            )
            tls = (
                "tls" in proxy_configuration_dict
                and proxy_configuration_dict["tls"] != "none"
            )
            alpn = (
                proxy_configuration_dict["alpn"]
                if "alpn" in proxy_configuration_dict
                else ["http/1.1"]
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

            proxy_component = self._get_tool_component_by_vmess(
                tool_type,
                proxy_name,
                uid,
                address,
                int(port),
                int(aid),
                cipher,
                network,
                tls,
                alpn=alpn,
                sni=sni,
                ws_option=ws_option,
            )
            return proxy_component

        if proxy_protocol == "vless":
            proxy_configuration_dict = literal_eval(proxy_configuration)
            proxy_name = proxy_configuration_dict["ps"]
            uid = proxy_configuration_dict["id"]
            address = proxy_configuration_dict["add"]
            port = proxy_configuration_dict["port"]
            flow = proxy_configuration_dict["flow"]
            network = (
                proxy_configuration_dict["type"]
                if "type" in proxy_configuration_dict
                else "tcp"
            )
            tls = (
                "security" in proxy_configuration_dict
                and proxy_configuration_dict["security"] == "tls"
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

            proxy_component = self._get_tool_component_by_vless(
                tool_type,
                proxy_name,
                uid,
                address,
                int(port),
                flow,
                network,
                tls,
                sni=sni,
                ws_option=ws_option,
            )
            return proxy_component

    def get_proxies(self, tool_type: str) -> list:
        """
        Get proxies
        """
        proxies = []

        proxy_links = []

        if "," in self.sub_url:
            for i in self.sub_url.split(","):
                r = self.get_method(decode_base64_str(i))
                proxy_links.extend(decode_base64_str(r.text).split("\n"))
        else:
            r = self.get_method(decode_base64_str(self.sub_url))
            proxy_links.extend(decode_base64_str(r.text).split("\n"))

        if self.custom_link is not None:
            custom_links_decoded = [
                decode_base64_str(i) for i in self.custom_link.split(",")
            ]
        else:
            custom_links_decoded = []

        proxy_links.extend(custom_links_decoded)

        for proxy_link in proxy_links:
            proxy_protocol, proxy_configuration, proxy_name = self._decode_sub_link(
                proxy_link
            )
            proxy = self.get_proxy_component(
                tool_type, proxy_protocol, proxy_configuration, proxy_name
            )
            if len(proxy) != 0:
                proxies.append(proxy)

        return proxies
