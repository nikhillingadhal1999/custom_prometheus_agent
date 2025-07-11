from flask import Flask, request, jsonify, Response
from flexmetric.metric_process.expiring_queue import metric_queue
import argparse
from prometheus_client import generate_latest, REGISTRY, CONTENT_TYPE_LATEST

app = Flask(__name__)


@app.route('/metrics')
def metrics():
    return Response(generate_latest(REGISTRY), mimetype=CONTENT_TYPE_LATEST)


def add_update_metric_route():
    @app.route("/update_metric", methods=["POST"])
    def update_metric():
        try:
            data = request.get_json(force=True)

            # Top-level validation
            if not isinstance(data, dict):
                return jsonify({"status": "invalid structure", "error": "Top-level JSON must be an object"}), 400

            required_keys = {"result", "labels", "main_label"}
            if not required_keys.issubset(data):
                return jsonify({"status": "invalid structure", "error": f"Missing keys: {required_keys - set(data)}"}), 400

            result = data.get("result")
            labels = data.get("labels")
            main_label = data.get("main_label")

            # Type validation
            if not isinstance(result, list) or not all(isinstance(item, dict) for item in result):
                return jsonify({"status": "invalid result", "error": "Result must be a list of dictionaries"}), 400

            if not isinstance(labels, list) or not all(isinstance(label, str) for label in labels):
                return jsonify({"status": "invalid labels", "error": "Labels must be a list of strings"}), 400

            if not isinstance(main_label, str) or not main_label.strip():
                return jsonify({"status": "invalid main_label", "error": "main_label must be a non-empty string"}), 400

            for idx, item in enumerate(result):
                if "label" not in item or "value" not in item:
                    return jsonify({"status": "invalid result item", "error": f"Item {idx} missing 'label' or 'value'"}), 400

                label_values = item["label"]
                value = item["value"]

                if not isinstance(label_values, list) or not all(isinstance(lv, str) for lv in label_values):
                    return jsonify({"status": "invalid label", "error": f"Item {idx} 'label' must be list of strings"}), 400

                if len(label_values) != len(labels):
                    return jsonify({
                        "status": "label count mismatch",
                        "error": f"Item {idx} label count ({len(label_values)}) does not match labels length ({len(labels)})"
                    }), 400

                try:
                    float(value)  # Validate numeric value
                except (ValueError, TypeError):
                    return jsonify({"status": "invalid value", "error": f"Item {idx} value must be numeric"}), 400

            # If all checks pass, queue the metric
            metric_queue.put(data)
            print("Queued:", data)

            return jsonify({"status": "success"}), 200

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500


def run_flask(host, port):
    app.run(host=host, port=port)
def secure_flask_run(args):
    app.run(host=args.host, port=args.port, ssl_context=(args.ssl_cert, args.ssl_key))