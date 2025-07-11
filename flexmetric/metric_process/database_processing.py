import yaml
import re
from flexmetric.metric_process.database_connections import create_clickhouse_client,create_sqlite_client,create_postgres_client
from flexmetric.metric_process.queries_execution import execute_clickhouse_command,execute_sqlite_query,execute_postgres_query
from flexmetric.logging_module.logger import get_logger
logger = get_logger(__name__)

logger.info("query execution")


def read_yaml_file(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def get_database_config(databases, db_name):
    for db in databases:
        if db["name"] == db_name:
            return db
    raise ValueError(
        f"[ERROR] Database config for '{db_name}' not found in database.yaml."
    )



def is_safe_query(query):
    cleaned_query = query.strip().lower()
    return re.match(r"^\(*\s*select", cleaned_query) is not None


def read_yaml_file(filepath: str) -> dict:
    try:
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise Exception(f"Error reading {filepath}: {e}")


def create_clients_from_config(config_file: str):
    db_configs = read_yaml_file(config_file).get('databases', [])
    clients = {}

    for db_conf in db_configs:
        db_id = db_conf.get('id')
        logger.info(db_id)
        db_type = db_conf.get('type')

        if not db_id:
            logger.info(f"Skipping unnamed database block: {db_conf}")
            continue

        try:
            if db_type == 'clickhouse':
                client = create_clickhouse_client(db_conf)
                clients[db_id] = client
                logger.info(clients)

            elif db_type == 'sqlite':
                client = create_sqlite_client(db_conf)
                clients[db_id] = client
                logger.info(clients)
            elif db_type == 'postgres':
                client = create_postgres_client(db_conf)
                clients[db_id] = client
                logger.info(clients)
            else:
                logger.info(f"Unsupported database type: {db_type}")

        except Exception as e:
            logger.error(f"Failed to create client '{db_id}': {e}")
    return clients

def process_and_get_value(cmd,rows_data,column_names):
    labels = cmd.get('labels', [])
    value_column = cmd.get('value_column', [])
    label_values = cmd.get('label_values', [])
    main_label = cmd.get('main_label', 'default_db_metric')
    missing_columns = [col for col in labels + [value_column] if col not in column_names]
    if missing_columns:
        raise ValueError(f"Missing columns in result: {missing_columns}")
    rows = []
    for row in rows_data:
        label_values = [str(row[column_names.index(col)]) for col in labels]
        value = row[column_names.index(value_column)]

        rows.append({
            'label': label_values,
            'value': value
        })

    return {
        'result': rows,
        'labels': labels,
        'main_label': main_label
    }

def execute_commands(clients: dict, commands_file: str):
    commands = read_yaml_file(commands_file).get('commands', [])
    results = []
    for cmd in commands:
        print("CMD : ",cmd)
        if cmd == None:
            continue
        cmd_id = cmd.get('id')
        db_id = cmd.get('database_id')
        db_type = cmd.get('type')
        query = cmd.get('query')
        if not cmd_id or not db_id or not db_type or not query:
            logger.info(f"Missing required fields in command '{cmd_id}'")
            continue

        client = clients.get(db_id)
        logger.info(clients)
        logger.info(db_id)
        logger.info(client)
        if not client:
            logger.info(f"No client for database_id '{db_id}' in command '{cmd_id}'")
            continue
        try:
            if db_type == 'clickhouse':
                logger.info("In clickhouse")
                response,column_names = execute_clickhouse_command(client,query)
                result = process_and_get_value(cmd,response,column_names)
                results.append(result)
            elif db_type == 'sqlite':
                response ,column_names = execute_sqlite_query(client,query)
                result = process_and_get_value(cmd,response,column_names)
                results.append(result)
            elif db_type == 'postgres':
                response ,column_names = execute_postgres_query(client,query)
                result = process_and_get_value(cmd,response,column_names)
                results.append(result)
            else:
                logger.info(f"Unknown type '{db_type}' in command '{cmd_id}'")
                continue
        except Exception as e:
            logger.error(f"Command '{cmd_id}' failed: {e}")
    return results


def process_database_queries(queries_file, databases_file):
    try:
        client_configs = create_clients_from_config(databases_file)
        return execute_commands(clients=client_configs,commands_file=queries_file)
    except Exception as ex:
        logger.error(f"Exception : {ex}")