from prometheus_client import Gauge, start_http_server
import psutil
import time
import sys
import os
from flexmetric.config.configuration import CA_PATH, CERT_PATH, KEY_PATH
from flexmetric.logging_module.logger import get_logger
from flexmetric.file_recognition.exec_file import execute_functions
from flexmetric.metric_process.process_commands import process_commands
from flexmetric.metric_process.database_processing import process_database_queries
from flexmetric.metric_process.expiring_queue import metric_queue
import argparse
import os
from flexmetric.metric_process.views import run_flask
import sched
import threading

scheduler = sched.scheduler(time.time, time.sleep)


def arguments():
    parser = argparse.ArgumentParser(
        description="FlexMetric: A flexible Prometheus exporter for commands, databases, scripts, and Python functions."
    )

    # Input type flags
    parser.add_argument(
        "--database",
        action="store_true",
        help="Process database.yaml and queries.yaml to extract metrics from databases.",
    )
    parser.add_argument(
        "--commands",
        action="store_true",
        help="Process commands.yaml to extract metrics from system commands.",
    )
    parser.add_argument(
        "--functions",
        action="store_true",
        help="Process Python functions from the provided path to extract metrics.",
    )
    parser.add_argument(
        "--expose-api",
        action="store_true",
        help="Expose Flask API to receive external metric updates.",
    )

    # Config file paths
    parser.add_argument(
        "--database-config",
        type=str,
        default=None,
        help="Path to the database configuration YAML file.",
    )
    parser.add_argument(
        "--queries-config",
        type=str,
        default=None,
        help="Path to the database queries YAML file.",
    )
    parser.add_argument(
        "--commands-config",
        type=str,
        default=None,
        help="Path to the commands configuration YAML file.",
    )
    parser.add_argument(
        "--functions-dir", type=str, default=None, help="Path to the python files dir."
    )
    parser.add_argument(
        "--functions-file",
        type=str,
        default=None,
        help="Path to the file containing which function to execute",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="port on which exportor runs"
    )
    parser.add_argument(
        "--flask-host",
        type=str,
        default="0.0.0.0",
        help="The hostname or IP address on which to run the Flask server (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--flask-port",
        type=int,
        default=5000,
        help="The port number on which to run the Flask server (default: 5000)",
    )

    return parser.parse_args()


logger = get_logger(__name__)

logger.info("prometheus is running")


def convert_to_data_type(value):
    if isinstance(value, str) and "%" in value:
        return float(value.strip("%"))
    elif isinstance(value, str) and ("GB" in value or "MB" in value):
        return float(value.split()[0].replace(",", ""))
    return value


gauges = {}


def validate_required_files(mode_name, required_files):
    missing = [desc for desc, path in required_files.items() if path == None]
    if missing:
        print(f"Missing {', '.join(missing)} for '{mode_name}' mode. Skipping...")
        return False

    return True


def validate_all_modes(args):
    """
    Validates all selected modes and their required files.

    Args:
        args: Parsed command-line arguments.

    Returns:
        bool: True if at least one valid mode is properly configured, False otherwise.
    """
    has_valid_mode = False

    mode_validations = [
        (
            args.database,
            "database",
            {
                "database-config": args.database_config,
                "queries-config": args.queries_config,
            },
        ),
        (args.commands, "commands", {"commands-config": args.commands_config}),
        (
            args.functions,
            "functions",
            {
                "functions-dir": args.functions_dir,
                "functions-file": args.functions_file,
            },
        ),
        (args.expose_api, "expose-api", {})
    ]

    for is_enabled, mode_name, files in mode_validations:
        if is_enabled:
            if validate_required_files(mode_name, files):
                has_valid_mode = True

    return has_valid_mode


def measure(args):
    exec_result = []
    queue_items = metric_queue.pop_all()
    print("QUEUE_ITEMS : ", queue_items)
    if len(queue_items) != 0:
        exec_result.extend(queue_items)
    if args.database:
        db_results = process_database_queries(args.queries_config, args.database_config)
        exec_result.extend(db_results)
    if args.functions:
        function_results = execute_functions(args.functions_dir, args.functions_file)
        exec_result.extend(function_results)
    if args.commands:
        cmd_results = process_commands(args.commands_config)
        if cmd_results != None:
            exec_result.extend(cmd_results)
    global gauges
    for data in exec_result:
        results = data["result"]
        labels = data["labels"]
        gauge_name = "_".join(labels).lower() + "_gauge"
        # print(labels)
        if gauge_name not in gauges:
            gauge = Gauge(gauge_name, f"{gauge_name} for different metrics", labels)
            gauges[gauge_name] = gauge
        else:
            gauge = gauges[gauge_name]
        for result in results:
            print(result, isinstance(result["label"], list))
            if isinstance(result["label"], str):
                try:
                    gauge.labels(result["label"]).set(
                        convert_to_data_type(result["value"])
                    )
                except Exception as ex:
                    logger.error("Cannot pass string")
            elif isinstance(result["label"], list):
                label_dict = dict(zip(labels, result["label"]))
                gauge.labels(**label_dict).set(convert_to_data_type(result["value"]))


def scheduled_measure(args):
    measure(args)
    scheduler.enter(5, 1, scheduled_measure, (args,))


def start_scheduler(args):
    scheduler.enter(0, 1, scheduled_measure, (args,))
    scheduler.run()


def main():
    args = arguments()
    print("Validating configuration...")
    if not validate_all_modes(args):
        print("No valid modes with proper configuration found. Exiting.")
        exit(1)

    print(f"Starting Prometheus metrics server on port {args.port}...")
    print("Starting server")
    start_http_server(args.port)
    scheduler_thread = threading.Thread(
        target=start_scheduler, args=(args,), daemon=True
    )
    scheduler_thread.start()
    if args.expose_api:
        run_flask(args.flask_host, args.flask_port)
    else:
        while True:
            time.sleep(2)


main()
