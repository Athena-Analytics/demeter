"""
Flask App
"""

import logging
import os
import traceback

from dotenv import load_dotenv
from flask import Flask, Response, request

from demeter.remote_proxy_config import RemoteProxyConfig
from demeter.utils import get_config

app = Flask(__name__)

logging.basicConfig(
    filename=os.getcwd() + "/log/demeter.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s",
)


@app.route("/tool_type/<tool_type>", methods=["GET"])
def remote_config(tool_type: str) -> Response:
    """
    Get remote config
    """
    try:
        log_data = {
            "method": request.method,
            "path": request.path,
            "args": request.args,
            "data": request.data.decode("utf-8"),
        }
        app.logger.info(log_data)

        config = get_config()
        sub_url = config["Proxy.Link"]["sub_url"]
        custom_link = config["Proxy.Link"]["custom_link"]
        r2_url = config["R2.Config-template"]["r2_url"]
        access_key = config["R2.Config-template"]["access_key"]
        secret_key = config["R2.Config-template"]["secret_key"]
        app.logger.info({"sub_url": sub_url, "custom_link": custom_link})

        remote_proxy_config = RemoteProxyConfig(
            tool_type, sub_url, custom_link, r2_url, access_key, secret_key
        )
        proxy_config = remote_proxy_config.get_remote_proxy_config()

        if tool_type == "singbox":
            content_type = "application/json; charset=utf-8"
        else:
            content_type = "text/plain; charset=utf-8"

        response = Response(proxy_config, content_type=content_type)

        return response
    except Exception as e:
        traceback.print_exc()
        app.logger.error(e)
        return str(e)


if __name__ == "__main__":
    load_dotenv()
    app.run(host="0.0.0.0", debug=True if os.getenv("FLASK_ENV") == "dev" else False)
