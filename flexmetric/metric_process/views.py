from flask import Flask, request, jsonify
from flexmetric.metric_process.expiring_queue import metric_queue
import argparse

app = Flask(__name__)


@app.route("/update_metric", methods=["POST"])
def update_metric():
    try:
        data = request.get_json()

        if not data or "result" not in data or not isinstance(data["result"], list):
            return jsonify({"status": "no"}), 400

        for item in data["result"]:
            if "label" not in item or "value" not in item:
                return jsonify({"status": "no"}), 400

        metric_queue.put(data)
        print(metric_queue)
        return jsonify({"status": "success"}), 200

    except Exception:
        return jsonify({"status": "no"}), 500


def run_flask(host, port):
    app.run(host=host, port=port)