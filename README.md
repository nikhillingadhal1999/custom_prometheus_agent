FlexMetric is a lightweight, pluggable, and extensible Prometheus exporter that helps you collect, expose, and visualize custom metrics with minimal setup and maximum flexibility.

With FlexMetric, you can:

Run system commands and expose their output as metrics

Execute SQL queries against databases like SQLite, PostgreSQL, and ClickHouse

Call custom Python functions and export their results

Receive externally submitted metrics via a secure Flask-based API with optional HTTPS (TLS)

All metrics are exposed in Prometheus-compatible format, making them ready for visualization in Grafana or any Prometheus-based monitoring stack.
---

Paste your rich text content here. You can paste directly from Word or other rich text sources.

*   Run **shell commands** and expose the results as **Prometheus metrics**.  
    ➔ _Harmful commands (e.g., file deletion, system shutdown) are blocked for safety._
    
*   Execute **SQL queries** and monitor database statistics:
    
    * **SQLite** (lightweight, file-based databases)
    * **PostgreSQL** (robust, production-grade relational databases)
    * **ClickHouse** (high-performance, analytical databases)  
* Potentially dangerous queries (e.g., `DROP`, `DELETE`, `TRUNCATE`) are blocked by default.
*   Automatically discover and expose **Python function outputs** as metrics.
*   Expose an optional **Flask API** (`/update_metric`) to receive and update external metrics **dynamically**.
*   Modular and **easy to extend**—add your own **custom integrations** with minimal effort.
*   Built-in **Prometheus-compatible HTTP server** (`/metrics`) with configurable port.
*   Supports **HTTPS** to securely expose both the metrics endpoint and API. 
*   Input **sanitization and validation** ensure only safe commands and queries are executed.

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
flexmetric --expose-api --port <port> --host <host>
```

## Example: Running FlexMetric with Flask API

To run FlexMetric with both Prometheus metrics and the Flask API enabled:

```bash
flexmetric --expose-api --port 5000 --host 0.0.0.0
```

Prometheus metrics exposed at:
http://localhost:5000/metrics

Flask API exposed at:
http://localhost:5000/update_metric

### Submitting a Metric to the Flask API
```bash
curl -X POST http://localhost:5000/update_metric \
-H "Content-Type: application/json" \
-d '{
  "result": [
    { 
      "label": ["cpu", "core_1"], 
      "value": 42.5 
    }
  ],
  "labels": ["metric_type", "core"],
  "main_label": "cpu_usage_metric"
}'

```

### Using flex metrics in secure mode

```bash
flexmetric --port 5000 --host 0.0.0.0 --enable-https --ssl-cert=cert.pem --ssl-key=key.pem
```
Prometheus metrics exposed at:
https://localhost:5000/metrics

Flask API exposed at:
https://localhost:5000/update_metric

### Submitting a Metric to the Flask API
```bash
curl -k -X POST https://localhost:5000/update_metric \
-H "Content-Type: application/json" \
-d '{
  "result": [
    { 
      "label": ["cpu", "core_1"], 
      "value": 42.5 
    }
  ],
  "labels": ["metric_type", "core"],
  "main_label": "cpu_usage_metric"
}'
```

### commands.yaml

```yaml
commands:
  - name: disk_usage
    command: df -h
    main_label: disk_usage_filesystem_mount_point
    labels: ["filesystem", "mounted"]
    label_columns: [0, -1]
    value_column: 4
    timeout_seconds: 60
```
Example to select label_column and value_column

```bash
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        50G   20G   28G  42% /
/dev/sdb1       100G   10G   85G  10% /data
```
## Fields description

| Field             | Description                                                                                                                |
|-------------------|----------------------------------------------------------------------------------------------------------------------------|
| `name`            | A **nickname** you give to this check. It's just for your reference to know what this command is doing (e.g., `"disk_usage"`). |
| `command`         | The **actual shell command** to run (e.g., `"df -h"`). It fetches the data you want to monitor.                             |
| `main_label`      | The **metric name** that will appear in Prometheus. This is what you will query to see the metric values.                  |
| `labels`          | A list of **label names** used to describe different dimensions of the metric (e.g., `["filesystem", "mounted"]`).         |
| `label_columns`   | A list of **column indexes** from the command’s output to extract the label values (e.g., `[0, -1]` for first and last column). |
| `value_column`    | The **column index** from the command's output to extract the **numeric value** (the actual metric value, e.g., disk usage). |
| `timeout_seconds` | Maximum time (in seconds) to wait for the command to complete. If it exceeds this time, the command is aborted.             |

## Database mode
## 🔗 Supported Database Connections

FlexMetric supports fetching and exposing metrics from multiple databases using a simple YAML-based configuration. This allows you to monitor data directly from your existing data sources without writing custom code.

### ✅ Currently Supported Databases:

| Database      | Type Name     | Description                                      |
|--------------|---------------|--------------------------------------------------|
| **SQLite**    | `sqlite`      | Lightweight, file-based relational database       |
| **PostgreSQL** | `postgres`    | Robust, production-grade relational database      |
| **ClickHouse** | `clickhouse`  | High-performance, analytical columnar database    |

---

### 📄 Example `database.yaml` Configuration:
file - database.yaml
```yaml
databases:
  - id: "local_sqlite"
    type: "sqlite"
    db_connection: "/path/to/example.db"

  - id: "analytics_pg"
    type: "postgres"
    host: "localhost"
    port: 5432
    database: "metricsdb"
    username: "postgres"
    password: "postgres_password"
    sslmode: "disable"
    client_cert: "/path/to/cert.pem"
    client_key: "/path/to/key.pem"
    ca_cert: "/path/to/ca.pem"

  - id: "clickhouse_cluster"
    type: "clickhouse"
    host: "localhost"
    port: 8443
    username: "default"
    password: "clickhouse_password"
    secure: true
    client_cert: "/path/to/cert.pem"
    client_key: "/path/to/key.pem"
    ca_cert: "/path/to/ca.pem"
```

## Supported Query Configuration

FlexMetric allows you to define custom queries in a simple YAML format. Each query is linked to a database using the `database_id` and can expose the results as Prometheus metrics with flexible labeling and value extraction.

### Example `queries.yaml` Configuration:

```yaml
commands:
  - id: "active_user_count_pg"
    type: "postgres"
    database_id: "analytics_pg"
    query: |
      SELECT
        country AS country_name,
        COUNT(*) AS active_user_count
      FROM users
      WHERE is_active = true
      GROUP BY country;
    main_label: "active_user_count"
    labels: ["country_name"]
    value_column: "active_user_count"

  - id: "total_user_count_sqlite"
    type: "sqlite"
    database_id: "local_sqlite"
    query: |
      SELECT
        'all' AS user_group,
        COUNT(*) AS total_user_count
      FROM users;
    main_label: "total_user_count"
    labels: ["user_group"]
    value_column: "total_user_count"

  - id: "clickhouse_user_summary"
    type: "clickhouse"
    database_id: "clickhouse_cluster"
    query: |
      SELECT
        region AS region_name,
        COUNT() AS user_count
      FROM users
      WHERE status = 'active'
      GROUP BY region;
    main_label: "clickhouse_user_count"
    labels: ["region_name"]
    value_column: "user_count"
```
## Functions mode

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
        { 'label': [label_value1, label_value2, ...], 'value': numeric_value }
    ],
    'labels': [label_name1, label_name2, ...],
    'main_label': 'your_main_metric_name'
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
| `--expose-api`       | Enable Flask API mode to receive external metrics         |                            |
| `--flask-port`       | Port for the Flask API (`/update_metric`)                 | `5000`                     |
| `--flask-host`       | Hostname for the Flask API                                | `0.0.0.0`                  |
| `--enable-https`     | Enable HTTPS for the Flask API                            |                            |
| `--ssl-cert`         | Path to SSL certificate file (`cert.pem`)                 |                            |
| `--ssl-key`          | Path to SSL private key file (`key.pem`)                  |                            |

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