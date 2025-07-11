import clickhouse_connect
import sqlite3
from flexmetric.logging_module.logger import get_logger
import os
import psycopg2


logger = get_logger(__name__)
logger.info("database logs")

def create_postgres_client(db_conf: dict):
    host = db_conf.get('host', 'localhost')
    port = db_conf.get('port', 5432)
    database = db_conf.get('database')
    username = db_conf.get('username', 'postgres')
    password = db_conf.get('password', '')

    sslmode = db_conf.get('sslmode', 'prefer')
    sslcert = db_conf.get('client_cert')
    sslkey = db_conf.get('client_key')
    sslrootcert = db_conf.get('ca_cert')

    if not database:
        raise ValueError("Missing 'database' name in PostgreSQL configuration")

    conn_params = {
        'host': host,
        'port': port,
        'dbname': database,
        'user': username,
        'password': password,
        'sslmode': sslmode
    }

    if sslcert and sslkey and sslrootcert:
        if not (os.path.isfile(sslcert) and os.path.isfile(sslkey) and os.path.isfile(sslrootcert)):
            raise FileNotFoundError("One or more SSL certificate files not found.")
        conn_params.update({
            'sslcert': sslcert,
            'sslkey': sslkey,
            'sslrootcert': sslrootcert,
            'sslmode': 'verify-full'
        })

    try:
        conn = psycopg2.connect(**conn_params)
        logger.info(f"PostgreSQL connection to '{database}' established successfully (SSL: {'Yes' if 'sslcert' in conn_params else 'No'})")
        return conn

    except Exception as e:
        logger.error(f"Failed to create PostgreSQL client: {e}")
        raise

def create_clickhouse_client(db_conf):
    id = db_conf.get('id')
    host = db_conf.get('host', 'localhost')
    port = db_conf.get('port', 9440)
    username = db_conf.get('username', 'default')
    password = db_conf.get('password', '')

    client_cert = db_conf.get('client_cert')
    client_cert_key = db_conf.get('client_key')
    ca_cert = db_conf.get('ca_cert')

    secure = bool(client_cert and client_cert_key and ca_cert)

    settings = {
        'host': host,
        'port': port,
        'username': username,
        'password': password,
        'secure': secure,
        'verify': False
    }

    if secure:
        settings.update({
            'client_cert': client_cert,
            'client_cert_key': client_cert_key,
            'ca_cert': ca_cert,
        })

    client = clickhouse_connect.get_client(**settings)
    logger.info(f"Clickhouse connection '{id}' created")
    return client


def create_sqlite_client(db_conf: dict):
    db_path = db_conf.get('db_connection')
    db_name = db_conf.get('db_name', 'default_sqlite_db')

    if not db_path or not os.path.isfile(db_path):
        raise FileNotFoundError(f"SQLite database file not found at {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        logger.info(f"SQLite connection '{db_name}' created")
        return conn
    except Exception as e:
        raise ConnectionError(f"Failed to create SQLite client: {e}")
