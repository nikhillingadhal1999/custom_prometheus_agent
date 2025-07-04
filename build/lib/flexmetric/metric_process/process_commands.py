import subprocess
import yaml
import re

# 1. Read YAML commands
def read_commands_from_yaml(file_path):
    with open(file_path, 'r') as f:
        config = yaml.safe_load(f)
    return config.get('commands', [])

# 2. Execute command with timeout
def execute_command_with_timeout(command, timeout):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            return ''
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return ''

def process_commands(config_file):
    commands = read_commands_from_yaml(config_file)
    all_results = []

    for cmd_info in commands:
        command = cmd_info['command']
        label_name = cmd_info['label']
        timeout = cmd_info.get('timeout_seconds', 30)
        label_column = cmd_info.get('label_column', -1)
        value_column = cmd_info.get('value_column', 0)
        fixed_label_value = cmd_info.get('label_value')

        raw_output = execute_command_with_timeout(command, timeout)
        lines = raw_output.strip().splitlines()

        result_list = []

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

            result_list.append({
                'label': label,
                'value': value
            })

        formatted = {
            'result': result_list,
            'labels': [label_name]
        }
        all_results.append(formatted)

    return all_results


# # Example usage:
# if __name__ == "__main__":
#     results = process_commands('/Users/nlingadh/code/custom_prometheus_agent/src/commands.yaml')
#     print(results)
