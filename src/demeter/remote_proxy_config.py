"""Remote proxy config method"""

import json
import re

import yaml

from demeter.fetch.cf import CF
from demeter.fetch.proxy_config import ProxyConfig


class RemoteProxyConfig:
    """
    Class remote proxy config
    """

    def __init__(
        self, tool_type, sub_url, custom_link, r2_url, access_key, secret_key
    ) -> None:
        self.tool_type = tool_type
        self.proxy_config = ProxyConfig(sub_url, custom_link)
        self.cf = CF(r2_url, access_key, secret_key)

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

        def _replace_jms_template(template: str, j: list) -> list:
            if "JMS" in template:
                j_number = template.split("-")[1]
                j_result = list(filter(lambda x: j_number in x, j))

                return j_result[0]

            return template

        jms = [p[name_key] for p in temp_config[proxy_key] if "JMS" in p[name_key]]

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

                group[proxy_key] = [
                    _replace_jms_template(i, jms) for i in group[proxy_key]
                ]

            if "default" in group and "JMS" in group["default"]:
                group["default"] = _replace_jms_template(group["default"], jms)

            _new.append(group)

        temp_config[proxy_group_key] = _new

        return temp_config

    def clash_remote_proxy_config(self):
        """
        Get clash remote proxy config
        """
        proxies = self.proxy_config.get_proxies(self.tool_type)
        clash_file = self.cf.get_file_from_r2(f"{self.tool_type}.yaml")

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
        singbox_file = self.cf.get_file_from_r2(f"{self.tool_type}.json")

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
        shadowrocket_file = self.cf.get_file_from_r2(f"{self.tool_type}.conf")
        return shadowrocket_file
