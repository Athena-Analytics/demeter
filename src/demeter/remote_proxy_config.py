"""Remote proxy config method"""

import json
import re

import yaml

from demeter.fetch.cf import CF
from demeter.fetch.proxy_config import ProxyConfig
from demeter.utils import get_config

config = get_config()
SUB_URL = config["Proxy.Link"]["sub_url"]
CUSTOM_LINK = config["Proxy.Link"]["custom_link"]

R2_URL = config["R2.Config-template"]["r2_url"]
ACCESS_KEY = config["R2.Config-template"]["access_key"]
SECRET_KEY = config["R2.Config-template"]["secret_key"]


class RemoteProxyConfig:
    """
    Class of get all kinds of remote proxy config
    """

    def __init__(self, tool_type) -> None:
        self.tool_type = tool_type
        self.proxy_config = ProxyConfig(SUB_URL, CUSTOM_LINK)
        self.cf = CF(ACCESS_KEY, SECRET_KEY)

    def get_remote_proxy_config(self):
        """
        Get remote proxy config
        """
        if self.tool_type == "clash":
            remote_proxy_config = self.clash_remote_proxy_config()
        elif re.search("singbox", self.tool_type):
            remote_proxy_config = self.singbox_remote_proxy_config()
        elif self.tool_type == "shadowrocket":
            remote_proxy_config = self.shadowrocket_remote_proxy_config()
        else:
            raise ValueError(f"tool_type must be valid. but got {self.tool_type}")

        return remote_proxy_config

    @staticmethod
    def _replace_airport(
        temp_config: dict,
        name_key: str,
        proxy_key: str,
        proxy_group_key: str,
    ) -> dict:

        def _replace_default_for_singbox(o: dict, j: list) -> dict:
            if "default" in o and "JMS" in o["default"]:
                n = o["default"].split("-")[1]
                o["default"] = list(filter(lambda x: n in x, j))[0]
            return o

        jms = [c[name_key] for c in temp_config[proxy_key] if "JMS" in c[name_key]]

        _new = []
        for group in temp_config[proxy_group_key]:
            proxy_type = [
                "relay",
                "fallback",
                "url-test",
                "select",
                "urltest",
                "selector",
            ]
            if group["type"] in proxy_type and "JMS" in ",".join(group[proxy_key]):
                no_jms = list(
                    filter(lambda x: x if "JMS" not in x else None, group[proxy_key])
                )
                no_jms.extend(jms)
                group[proxy_key] = no_jms
                group = _replace_default_for_singbox(group, jms)

            _new.append(group)

        temp_config[proxy_group_key] = _new

        return temp_config

    def clash_remote_proxy_config(self):
        """
        Get clash remote proxy config
        """
        proxies = self.proxy_config.get_proxies(self.tool_type)
        clash_file = self.cf.get_file_from_r2(R2_URL, f"{self.tool_type}.yaml")

        clash_configuration_template = yaml.safe_load(clash_file)
        clash_configuration_template["proxies"] = proxies

        clash_configuration = self._replace_airport(
            clash_configuration_template, "name", "proxies", "proxy-groups"
        )

        yaml_data = yaml.dump(clash_configuration, allow_unicode=True)

        return yaml_data

    def singbox_remote_proxy_config(self):
        """
        Get sing-box remote proxy config
        """

        def add_proxy_chain(proxies: list):
            filter_proxy = list(filter(lambda x: x["tag"] == "Vless_vision", proxies))
            proxy_chain = filter_proxy[0].copy()
            proxy_chain["tag"] = "Proxy_chain"
            proxy_chain["detour"] = "airport_select"
            proxies.append(proxy_chain)
            return proxies

        proxies = add_proxy_chain(self.proxy_config.get_proxies(self.tool_type))
        singbox_file = self.cf.get_file_from_r2(R2_URL, f"{self.tool_type}.json")

        singbox_configuration_template = json.loads(singbox_file)
        singbox_configuration_template["outbounds"].extend(proxies)

        singbox_configuration = self._replace_airport(
            singbox_configuration_template, "tag", "outbounds", "outbounds"
        )

        json_data = json.dumps(singbox_configuration, indent=4)

        return json_data

    def shadowrocket_remote_proxy_config(self):
        """
        Get shadow rocket remote proxy config
        """
        shadowrocket_file = self.cf.get_file_from_r2(R2_URL, f"{self.tool_type}.conf")
        return shadowrocket_file
