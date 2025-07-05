# FlexMetric

FlexMetric is a lightweight, flexible, and extensible Prometheus exporter that allows you to expose system metrics, database query results, Python function outputs, and externally submitted metrics via an optional Flask API as Prometheus-compatible metrics—with minimal setup and maximum customization.

---

## Features

- Run shell commands and expose the results as Prometheus metrics.
- Execute SQL queries (e.g., SQLite) and monitor database statistics.
- Automatically discover and expose Python function outputs as metrics.
- Expose an optional **Flask API** (`/update_metric`) to receive external metrics dynamically.
- Modular and easy to extend—add your own custom integrations.
- Built-in Prometheus HTTP server (`/metrics`) with configurable port.

---

## Installation

Install from PyPI:

```bash
pip install flexmetric
```
## Usage

Run FlexMetric from the command line:

```bash
flexmetric --commands --commands-config commands.yaml --port 8000
```

## Available Modes

FlexMetric supports multiple modes that can be used individually or combined to expose metrics:

| Mode            | Description                                                            | Required Configuration File(s)           |
|-----------------|------------------------------------------------------------------------|------------------------------------------|
| `--commands`     | Runs system commands and exports outputs as Prometheus metrics.         | `commands.yaml`                          |
| `--database`     | Executes SQL queries on databases and exports results.                 | `database.yaml` and `queries.yaml`       |
| `--functions`    | Discovers and runs user-defined Python functions and exports outputs.  | `executable_functions.txt`               |
| `--expose-api`   | Exposes a Flask API (`/update_metric`) to receive external metrics.     | *No configuration file required*         |
### Example of Using Multiple Modes Together

```bash
flexmetric --commands --commands-config commands.yaml --database --database-config database.yaml --queries-config queries.yaml
```

## Configuration File Examples

Below are example configurations for each supported mode.

## Using the Flask API in FlexMetric

To use the Flask API for submitting external metrics, you need to start the agent with the `--expose-api` flag along with the Flask host and port.

### Start FlexMetric with Flask API

```bash
flexmetric --expose-api --flask-port <port> --flask-host <host> --metrics-port <metrics-port>
```

## Example: Running FlexMetric with Flask API

To run FlexMetric with both Prometheus metrics and the Flask API enabled:

```bash
flexmetric --expose-api --flask-port 5000 --flask-host 0.0.0.0 --port 8000
```

Prometheus metrics exposed at:
http://localhost:8000/metrics

Flask API exposed at:
http://localhost:5000/update_metric

### Submitting a Metric to the Flask API
```bash
curl -X POST http://localhost:5000/update_metric \
-H "Content-Type: application/json" \
-d '{
  "result": [
    { "label": "cpu_usage", "value": 42.5 }
  ],
  "labels": ["cpu"]
}'

```

### commands.yaml

```yaml
commands:
  - name: disk_usage
    command: df -h
    label: path
    timeout_seconds: 60
```
```yaml
databases:
  - name: mydb
    db_type: sqlite
    db_connection: /path/to/my.db
````
```yaml
queries:
  - name: user_count
    db_type: sqlite
    db_name: mydb
    query: "SELECT COUNT(*) FROM users;"
    label: table
    label_value: users
```
executable_functions.txt 
```
function_name_1
function_name_2
```

## Python Function Output Format

When using the `--functions` mode, each Python function you define is expected to return a dictionary in the following format:

```python
{
    'result': [
        {'label': <label_or_labels>, 'value': <numeric_value>}
    ],
    'labels': [<label_name_1>]
}
```

### Explanation:

| Key     | Description                                                               |
|--------|---------------------------------------------------------------------------|
| `result` | A list of dictionaries, each containing a `label` and a corresponding numeric `value`. |
| `labels` | A list of label names (used as Prometheus labels).                        |


## Command-Line Options

The following command-line options are available when running FlexMetric:

| Option              | Description                                              | Default                    |
|---------------------|----------------------------------------------------------|----------------------------|
| `--port`             | Port for the Prometheus metrics server (`/metrics`)      | `8000`                     |
| `--commands`         | Enable commands mode                                      |                            |
| `--commands-config`  | Path to commands YAML file                                | `commands.yaml`            |
| `--database`         | Enable database mode                                      |                            |
| `--database-config`  | Path to database YAML file                                | `database.yaml`            |
| `--queries-config`   | Path to queries YAML file                                 | `queries.yaml`             |
| `--functions`        | Enable Python functions mode                              |                            |
| `--functions-file`   | Path to functions file                                    | `executable_functions.txt` |
| `--scripts`          | Enable shell scripts mode                                 |                            |
| `--scripts-config`   | Path to scripts YAML file                                 | `scripts.yaml`             |
| `--expose-api`       | Enable Flask API mode to receive external metrics         |                            |
| `--flask-port`       | Port for the Flask API (`/update_metric`)                 | `5000`                     |
| `--flask-host`       | Hostname for the Flask API                                | `0.0.0.0`                  |
### Example Command:

```bash
flexmetric --commands --commands-config commands.yaml --port 8000
```
## Example Prometheus Output

Once FlexMetric is running, the `/metrics` endpoint will expose metrics in the Prometheus format.

Example output:
```bash
disk_usage_gauge{path="/"} 45.0
```

Each metric includes labels and numeric values that Prometheus can scrape and visualize.

---

## Future Enhancements

The following features are planned or under consideration to improve FlexMetric:

- Support for additional databases such as PostgreSQL and MySQL.
- Enhanced support for more complex scripts and richer label extraction.