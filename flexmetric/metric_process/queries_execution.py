from flexmetric.logging_module.logger import get_logger
logger = get_logger(__name__)

logger.info("query execution")

def execute_clickhouse_command(client, command: str):
    try:
        result = client.query(command)
        row_list = result.result_rows
        column_names = result.column_names
        return row_list,column_names
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return None
def execute_sqlite_query(conn, query):
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        return rows, column_names
    except Exception as ex:
        logger.error(f"Exception during SQLite query: {ex}")
        return [], []

def execute_postgres_query(conn, query):
    try:
        cursor = conn.cursor()
        cursor.execute(query)

        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

        logger.info(f"Query executed successfully. Rows fetched: {len(rows)}")

        return rows, column_names

    except Exception as ex:
        logger.error(f"Exception during Postgres query: {ex}")
        return [], []