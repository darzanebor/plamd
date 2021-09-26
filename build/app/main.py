#!/usr/bin/env python3
""" Plamd Probe  """

import json
from os import environ as env
from icmplib import ping
from icmplib.exceptions import (
    ICMPSocketError,
    NameLookupError,
    SocketAddressError,
    SocketPermissionError,
)
import json_log_formatter  # Used in gunicorn_logging.conf
from flask import Flask, request, make_response, abort
from flask_wtf.csrf import CSRFProtect
from prometheus_client import multiprocess, generate_latest, Summary, CollectorRegistry


app = Flask(__name__, template_folder="templates")
csrf = CSRFProtect()

app.config["PLAMD_COUNT"] = env.get("PLAMD_COUNT", 3)
app.config["PLAMD_TIMEOUT"] = env.get("PLAMD_TIMEOUT", 1)
app.config["PLAMD_INTERVAL"] = env.get("PLAMD_INTERVAL", 0.3)
app.config["PLAMD_LIMIT_COUNT"] = int(env.get("PLAMD_LIMIT_COUNT", 16))

REQUEST_TIME = Summary("plamd_request_processing_time", "Time spent processing request")


def child_exit(server, worker):
    """ multiprocess function for prometheus to track gunicorn """
    multiprocess.mark_process_dead(worker.pid)


@app.route("/healthz", methods=["GET"])
def default_healthz():
    """ healthcheck route """
    return make_response("", 200)


@app.route("/metrics", methods=["GET"])
def metrics():
    """  metrics route """
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return generate_latest(registry)


@app.route("/<path:path>", methods=["GET"])
@app.route("/<path:path>")
@REQUEST_TIME.time()
def req_handler(path):
    """requests handler"""
    try:
        if request.method == "GET":
            interval = float(
                request.args.get("interval", default=app.config["PLAMD_INTERVAL"])
            )
            timeout = float(
                request.args.get("timeout", default=app.config["PLAMD_TIMEOUT"])
            )
            count = int(request.args.get("count", default=app.config["PLAMD_COUNT"]))
            target = request.args.get("target", default=None)
            result = ping(
                count=count
                if count <= app.config["PLAMD_LIMIT_COUNT"]
                else int(app.config["PLAMD_COUNT"]),
                address=target,
                timeout=timeout,
                privileged=False,
                interval=interval,
            )
            return make_response(
                json.dumps(
                    {
                        "jitter": result.jitter,
                        "address": result.address,
                        "min_rtt": result.min_rtt,
                        "avg_rtt": result.avg_rtt,
                        "max_rtt": result.max_rtt,
                        "is_alive": result.is_alive,
                        "pkts_loss": result.packet_loss,
                        "pkts_sent": result.packets_sent,
                        "pkts_received": result.packets_received,
                    }
                ),
                200,
                {"Content-Type": "application/json; charset=utf-8", "Server": "Snooki"},
            )
        return make_response("", 405)
    except (
        NameLookupError,
        SocketPermissionError,
        SocketAddressError,
        ICMPSocketError,
    ) as exp:
        print("Error in req_handler() " + str(exp))
        return abort(500)


if __name__ == "__main__":
    app.run(threaded=True)
    csrf.init_app(app)
