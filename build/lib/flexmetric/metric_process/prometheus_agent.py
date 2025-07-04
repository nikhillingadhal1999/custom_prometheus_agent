from prometheus_client import Gauge, start_http_server
import psutil 
import time
import sys
import os

from flexmetric.config.configuration import CA_PATH , CERT_PATH, KEY_PATH
from flexmetric.logging_module.logger import get_logger
from flexmetric.file_recognition.exec_file import execute_functions
from flexmetric.metric_process.process_commands import process_commands
from flexmetric.metric_process.database_processing import process_database_queries
import argparse
import os
def arguments():
    parser = argparse.ArgumentParser(
        description='FlexMetric: A flexible Prometheus exporter for commands, databases, scripts, and Python functions.'
    )

    # Input type flags
    parser.add_argument('--database', action='store_true', help='Process database.yaml and queries.yaml to extract metrics from databases.')
    parser.add_argument('--commands', action='store_true', help='Process commands.yaml to extract metrics from system commands.')
    parser.add_argument('--functions', action='store_true', help='Process Python functions from the provided path to extract metrics.')
    

    # Config file paths
    parser.add_argument('--database-config', type=str, default=None, help='Path to the database configuration YAML file.')
    parser.add_argument('--queries-config', type=str, default=None, help='Path to the database queries YAML file.')
    parser.add_argument('--commands-config', type=str, default=None, help='Path to the commands configuration YAML file.')
    parser.add_argument('--functions-dir', type=str, default=None, help='Path to the python files dir.')
    parser.add_argument('--functions-file', type=str, default=None, help='Path to the file containing which function to execute')
    parser.add_argument('--port', type=int, default=8000, help='port on which exportor runs')

    return parser.parse_args()

logger = get_logger(__name__)

logger.info("prometheus is running") 

def convert_to_data_type(value):
    if isinstance(value, str) and '%' in value:
        return float(value.strip('%'))
    elif isinstance(value, str) and ('GB' in value or 'MB' in value):
        return float(value.split()[0].replace(',', ''))
    return value
gauges = []

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
        (args.database, 'database', {
            'database-config': args.database_config,
            'queries-config': args.queries_config
        }),
        (args.commands, 'commands', {
            'commands-config': args.commands_config
        }),
        (args.functions, 'functions', {
            'functions-dir': args.functions_dir,
            'functions-file':args.functions_file
        })
    ]

    for is_enabled, mode_name, files in mode_validations:
        if is_enabled:
            if validate_required_files(mode_name, files):
                has_valid_mode = True

    return has_valid_mode


def measure(init_flag,args):
    exec_result = []
    if args.database:
        db_results = process_database_queries(args.queries_config, args.database_config)
        exec_result.extend(db_results)
    if args.functions:
        function_results = execute_functions(args.functions_dir,args.functions_file)
        exec_result.extend(function_results)
    if args.commands:
        cmd_results = process_commands(args.commands_config)
        exec_result.extend(cmd_results)
    # exec_result = process_commands('commands.yaml')
    # print(exec_result)
    global gauges
    count = 0
    for data in exec_result:
        results= data['result']
        labels = data['labels']
        gauge_name = '_'.join(labels).lower() + "_gauge"
        print(labels)
        if init_flag:
            gauge = Gauge(gauge_name, f"{gauge_name} for different metrics", labels)
            gauges.append(gauge)
        else:
            gauge = gauges[count]
            count += 1
        for result in results:
            print(result,isinstance(result['label'],list))
            if isinstance(result['label'],str):
                try:
                    gauge.labels(result['label']).set(convert_to_data_type(result['value']))
                except Exception as ex:
                    logger.error("Cannot pass string")
            elif isinstance(result['label'],list):
                label_dict = dict(zip(labels, result['label']))
                gauge.labels(**label_dict).set(convert_to_data_type(result['value']))

if __name__ == "__main__":
    args = arguments()
    print("Validating configuration...")
    if not validate_all_modes(args):
        print("No valid modes with proper configuration found. Exiting.")
        exit(1)

    print(f"Starting Prometheus metrics server on port {args.port}...")
    print("Starting server")
    start_http_server(args.port)
    flag = True
    while True:
        measure(flag,args)
        flag = False
        time.sleep(5)
