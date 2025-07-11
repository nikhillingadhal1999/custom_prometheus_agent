import subprocess
import yaml
import re
from flexmetric.logging_module.logger import get_logger

logger = get_logger(__name__)

logger.info("prometheus is running") 

def read_commands_from_yaml(file_path):
    with open(file_path, 'r') as f:
        config = yaml.safe_load(f)
    return config.get('commands', [])

def execute_command_with_timeout(command, timeout):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            logger.info(f"Exception in running the command {command}")
            return ''
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return ''
    except Exception as ex:
        logger.error(f"Exception : {ex}")
        return ''

def parse_command_output(raw_output, label_column, value_column, fixed_label_value):
    result_list = []
    lines = raw_output.strip().splitlines()

    for line in lines:
        parts = line.strip().split()
        if not parts:
            continue

        if label_column == 'fixed':
            label = fixed_label_value or 'label'
        else:
            try:
                label = parts[label_column]
            except IndexError:
                label = 'unknown'

        try:
            raw_value = parts[value_column]
            cleaned_value = re.sub(r'[^\d\.\-]', '', raw_value)
            value = float(cleaned_value) if cleaned_value else 1
        except (IndexError, ValueError):
            value = 1

        result_list.append({'label': label, 'value': value})

    return result_list

def process_single_command(cmd_info):
    command = cmd_info['command']
    timeout = cmd_info.get('timeout_seconds', 30)
    labels = cmd_info.get('labels', [])
    label_columns = cmd_info.get('label_columns', [])
    value_column = cmd_info.get('value_column', 0)
    main_label = cmd_info.get('main_label', 'default_metric')

    raw_output = execute_command_with_timeout(command, timeout)
    if not raw_output:
        logger.warning(f"No results for command {command}")
        return None

    lines = raw_output.strip().split('\n')
    if not lines:
        logger.error(f"No valid lines returned from command: {command}")
        return None
    result_list = []
    for line in lines:
        parts = line.split()
        try:
            label_columns_value = []
            for value in label_columns:
                label_columns_value.append(parts[value])
            result_list.append({ "label": label_columns_value, "value": parts[value_column] })
        except Exception as e:
            logger.error(f"Error parsing line: '{line}' → {e}")
            continue
    return {
        'result': result_list,
        'labels': labels,
        'main_label': main_label
    }



def is_command_safe(command):
    blacklist = ['rm', 'reboot', 'shutdown', 'halt', 'poweroff', 'mkfs', 'dd']
    for dangerous_cmd in blacklist:
        if dangerous_cmd in command.split():
            return False
    return True

def process_commands(config_file):
    commands = read_commands_from_yaml(config_file)
    all_results = []

    for cmd_info in commands:
        command = cmd_info.get('command', '')
        if not command:
            logger.error("Command is missing in the configuration.")
            continue

        if not is_command_safe(command):
            logger.warning(f"Command '{command}' is not allowed and will not be executed.")
            continue

        try:
            formatted_result = process_single_command(cmd_info)
            if formatted_result:
                all_results.append(formatted_result)
        except KeyError as e:
            logger.error(f"Missing key in command configuration: {e}. Command: {cmd_info}")
        except Exception as e:
            logger.error(f"An error occurred while processing command '{command}': {e}")

    return all_results

# # Example usage:
# if __name__ == "__main__":
#     results = process_commands('/Users/nlingadh/code/custom_prometheus_agent/src/commands.yaml')
#     print(results)
