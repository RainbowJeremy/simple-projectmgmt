import sqlite3
from datetime import datetime
from config import Config

def get_db_connection():
    """Get a database connection with row factory set."""
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=None, fetch=False):
    """Execute a query with optional parameters."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()

def execute_many(query, params_list):
    """Execute a query multiple times with different parameters."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()

def get_table_schema(table_name):
    """Get the schema of a specific table."""
    query = f"PRAGMA table_info({table_name})"
    return execute_query(query, fetch=True)

def backup_database(backup_path):
    """Create a backup of the database."""
    try:
        source = sqlite3.connect(Config.DATABASE)
        backup = sqlite3.connect(backup_path)
        source.backup(backup)
        backup.close()
        source.close()
        return True
    except Exception as e:
        print(f"Backup failed: {e}")
        return False

def get_all_tables():
    """Get a list of all tables in the database."""
    query = "SELECT name FROM sqlite_master WHERE type='table'"
    tables = execute_query(query, fetch=True)
    return [table['name'] for table in tables]

def drop_table(table_name):
    """Drop a table from the database."""
    query = f"DROP TABLE IF EXISTS {table_name}"
    execute_query(query)

def table_exists(table_name):
    """Check if a table exists in the database."""
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
    result = execute_query(query, (table_name,), fetch=True)
    return len(result) > 0 