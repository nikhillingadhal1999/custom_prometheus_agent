import yaml
import sqlite3
import re

def read_yaml_file(file_path):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def get_database_config(databases, db_name):
    for db in databases:
        if db['name'] == db_name:
            return db
    raise ValueError(f"[ERROR] Database config for '{db_name}' not found in database.yaml.")

def execute_sqlite_query(db_path, query):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        conn.close()
        return float(result[0]) if result and result[0] is not None else None
    except Exception as e:
        print(f"[ERROR] SQLite query failed on {db_path}: {e}")
        return None

def is_safe_query(query):
    # Remove leading spaces and brackets
    cleaned_query = query.strip().lower()
    # Match only queries that start with "select"
    return re.match(r'^\(*\s*select', cleaned_query) is not None

def process_database_queries(queries_file, databases_file):
    # Get queries from queries file
    queries_config = read_yaml_file(queries_file)
    # Get database from database file
    databases_config = read_yaml_file(databases_file)

    commands = queries_config.get('commands', [])
    databases = databases_config.get('databases', [])

    all_results = []

    for cmd in commands:
        try:
            db_conf = get_database_config(databases, cmd['database'])

            if db_conf['db_type'] != 'sqlite':
                print(f"[WARN] Unsupported database type: {db_conf['db_type']} in command {cmd['name']}")
                continue

            db_path = db_conf['db_connection']
            query = cmd['query']
            label = cmd['label']
            label_value = cmd['label_value']
            # check if query is safe 
            if is_safe_query(query):
                value = execute_sqlite_query(db_path, query)
            else:
                print(f"[WARN] Unsupported query type: {query}")
                return None

            if value is not None:
                result = {
                    'result': [{'label': label_value, 'value': value}],
                    'labels': [label]
                }
                all_results.append(result)
            else:
                print(f"[INFO] No result for command '{cmd['name']}' on database '{cmd['database']}'")

        except Exception as e:
            print(f"[ERROR] Processing command '{cmd.get('name', 'unknown')}' failed: {e}")

    return all_results