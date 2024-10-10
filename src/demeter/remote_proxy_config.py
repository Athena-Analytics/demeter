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
        self.cf = CF(R2_URL, ACCESS_KEY, SECRET_KEY)

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
            raise ValueError("")

        return remote_proxy_config

    @staticmethod
    def _replace_airport_for_clash(proxy_config: dict) -> dict:

        jms_names = [
            proxy["name"] for proxy in proxy_config["proxies"] if "JMS" in proxy["name"]
        ]

        new_proxy_groups = []
        for proxy_group in proxy_config["proxy-groups"]:
            tmp_proxy_group = proxy_group.copy()
            proxies_names = ",".join(proxy_group["proxies"])

            if "JMS" in proxies_names:
                new_proxies = list(
                    filter(
                        lambda x: x if "JMS" not in x else None, proxy_group["proxies"]
                    )
                )

                new_proxies.extend(jms_names)
                tmp_proxy_group["proxies"] = new_proxies

                new_proxy_groups.append(tmp_proxy_group)
            else:
                new_proxy_groups.append(proxy_group)

        proxy_config["proxy-groups"] = new_proxy_groups

        return proxy_config

    @staticmethod
    def _replace_airport_for_singbox(proxy_config: dict) -> dict:

        def replace_default_jms(outbound: dict) -> dict:
            if "default" in outbound and "JMS" in outbound["default"]:
                jms_num = outbound["default"].split("-")[1]
                outbound["default"] = list(filter(lambda x: jms_num in x, jms_names))[0]
            return outbound

        jms_names = [
            outbound["tag"]
            for outbound in proxy_config["outbounds"]
            if "JMS" in outbound["tag"]
        ]

        new_outbounds = []
        for outbound in proxy_config["outbounds"]:
            if outbound["type"] in ["urltest", "selector"] and "JMS" in ",".join(
                outbound["outbounds"]
            ):
                new_proxies = list(
                    filter(
                        lambda x: x if "JMS" not in x else None, outbound["outbounds"]
                    )
                )
                new_proxies.extend(jms_names)
                outbound["outbounds"] = new_proxies
                outbound = replace_default_jms(outbound)

            new_outbounds.append(outbound)

        proxy_config["outbounds"] = new_outbounds
        return proxy_config

    def clash_remote_proxy_config(self):
        """
        Get clash remote proxy config
        """
        proxies = self.proxy_config.get_proxies(self.tool_type)

        clash_file = self.cf.get_file_from_r2(f"{self.tool_type}.yaml")
        clash_configuration_template = yaml.safe_load(clash_file)
        clash_configuration_template["proxies"] = proxies

        clash_configuration = self._replace_airport_for_clash(
            clash_configuration_template
        )

        yaml_data = yaml.dump(clash_configuration, allow_unicode=True)

        return yaml_data

    def singbox_remote_proxy_config(self):
        """
        Get sing-box remote proxy config
        """

        def add_proxy_chain(proxies: list):
            filter_proxy = list(filter(lambda x: x["tag"] == "Vmess_ws", proxies))
            proxy_chain = filter_proxy[0].copy()
            proxy_chain["tag"] = "Proxy_chain"
            proxy_chain["detour"] = "airport_select"
            proxies.append(proxy_chain)
            return proxies

        proxies = add_proxy_chain(self.proxy_config.get_proxies(self.tool_type))
        singbox_file = self.cf.get_file_from_r2(f"{self.tool_type}.json")

        singbox_configuration_template = json.loads(singbox_file)
        singbox_configuration_template["outbounds"].extend(proxies)

        singbox_configuration = self._replace_airport_for_singbox(
            singbox_configuration_template
        )

        json_data = json.dumps(singbox_configuration, indent=4)

        return json_data

    def shadowrocket_remote_proxy_config(self):
        """
        Get shadow rocket remote proxy config
        """
        shadowrocket_file = self.cf.get_file_from_r2(f"{self.tool_type}.conf")
        return shadowrocket_file
