"""
Flask App
"""

import logging
import os
import re
import traceback

from dotenv import load_dotenv
from flask import Flask, Response, request

from demeter.remote_proxy_config import RemoteProxyConfig
from demeter.utils import decode_base64_str, encode_base64_str, get_config

app = Flask(__name__)

logging.basicConfig(
    filename=os.getcwd() + "/log/demeter.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s",
)


@app.route("/health", methods=["GET"])
def health_check() -> Response:
    """
    Check if server is healthy
    """
    response = None
    try:
        log_data = {
            "method": request.method,
            "path": request.path,
            "args": request.args,
            "data": request.data.decode("utf-8"),
        }
        app.logger.info(log_data)

        response = Response("healthy")

        return response
    except Exception as e:
        traceback.print_exc()
        app.logger.error(e)
        response = Response("unhealthy", status=500)
        return response


@app.route("/encode/", methods=["GET"])
def encode() -> Response:
    """
    Encode something by base64
    """
    response = None
    try:
        log_data = {
            "method": request.method,
            "path": request.path,
            "args": request.args,
            "data": request.data.decode("utf-8"),
        }
        app.logger.info(log_data)

        s = request.args.get("s")

        if s is None:
            raise ValueError("Please provide a valid param")

        result = encode_base64_str(s)
        response = Response(result, content_type="text/plain; charset=utf-8")

        return response
    except ValueError as e:
        traceback.print_exc()
        app.logger.error(e)
        response = Response(str(e), status=400)
        return response
    except Exception as e:
        traceback.print_exc()
        app.logger.error(e)
        response = Response(str(e), status=500)
        return response


@app.route("/decode/", methods=["GET"])
def decode() -> Response:
    """
    Decode something by base64
    """
    response = None
    try:
        log_data = {
            "method": request.method,
            "path": request.path,
            "args": request.args,
            "data": request.data.decode("utf-8"),
        }
        app.logger.info(log_data)

        s = request.args.get("s")

        if s is None:
            raise ValueError("Please provide a valid param")

        result = decode_base64_str(s)
        response = Response(result, content_type="text/plain; charset=utf-8")

        return response
    except ValueError as e:
        traceback.print_exc()
        app.logger.error(e)
        response = Response(str(e), status=400)
        return response
    except Exception as e:
        traceback.print_exc()
        app.logger.error(e)
        response = Response(str(e), status=500)
        return response


@app.route("/tool_type/<tool_type>", methods=["GET"])
def remote_config(tool_type: str) -> Response:
    """
    Get remote config
    """
    response = None
    try:
        log_data = {
            "method": request.method,
            "path": request.path,
            "args": request.args,
            "data": request.data.decode("utf-8"),
        }
        app.logger.info(log_data)

        if re.search("singbox", tool_type):
            content_type = "application/json; charset=utf-8"
        elif tool_type in ["clash", "shadowrocket"]:
            content_type = "text/plain; charset=utf-8"
        else:
            raise ValueError("Please provide valid path")

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

        response = Response(proxy_config, content_type=content_type)

        return response
    except ValueError as e:
        traceback.print_exc()
        app.logger.error(e)
        response = Response(str(e), status=400)
        return response
    except Exception as e:
        traceback.print_exc()
        app.logger.error(e)
        response = Response(str(e), status=500)
        return response


if __name__ == "__main__":
    load_dotenv()
    app.run(host="0.0.0.0", debug=True if os.getenv("FLASK_ENV") == "dev" else False)
