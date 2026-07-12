# ============================================================
#  ENTERPRISE MANUFACTURING PLANNING SYSTEM (EMPS)
#  FILE    : config/database.py
#  PURPOSE : Database connection configuration and management
#  Author  : Prashant Yadav | Enrolment: 2450505390
#  Course  : MCSP-232 | IGNOU MCA
# ============================================================

import os
import pymysql
import pymysql.cursors
from dotenv import load_dotenv

# Load all environment variables from the .env file
# This keeps sensitive credentials out of source code
load_dotenv()


# ============================================================
#  CLASS: DatabaseConfig
#  Stores all DB connection parameters from environment
#  variables. Never hardcode credentials in source files.
# ============================================================
class DatabaseConfig:
    HOST     = os.getenv('DB_HOST',     'localhost')
    PORT     = int(os.getenv('DB_PORT', 3306))
    USER     = os.getenv('DB_USER',     'emps_app_user')
    PASSWORD = os.getenv('DB_PASSWORD', '')
    DATABASE = os.getenv('DB_NAME',     'emps_db')
    CHARSET  = 'utf8mb4'


# ============================================================
#  FUNCTION: get_connection()
#  Creates and returns a new PyMySQL database connection.
#  DictCursor makes rows return as {column: value} dicts.
#  autocommit=False enables manual transaction control.
# ============================================================
def get_connection():
    """
    Opens a new MySQL database connection using PyMySQL.
    Returns: pymysql.Connection object
    Raises : pymysql.MySQLError on connection failure
    """
    try:
        connection = pymysql.connect(
            host        = DatabaseConfig.HOST,
            port        = DatabaseConfig.PORT,
            user        = DatabaseConfig.USER,
            password    = DatabaseConfig.PASSWORD,
            database    = DatabaseConfig.DATABASE,
            charset     = DatabaseConfig.CHARSET,
            cursorclass = pymysql.cursors.DictCursor,
            autocommit  = False
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"[DB ERROR] Connection failed: {e}")
        raise


# ============================================================
#  FUNCTION: execute_query()
#  Safe helper for SELECT queries.
#  Uses parameterised %s placeholders to prevent SQL injection.
#  Always closes the connection in the finally block.
# ============================================================
def execute_query(query, params=None):
    """
    Executes a SELECT SQL query and returns all result rows.
    Parameters:
        query  (str)   : SQL query string with %s placeholders
        params (tuple) : Values to bind into the placeholders
    Returns:
        list of dict   : Query result rows
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            results = cursor.fetchall()
        return results
    except pymysql.MySQLError as e:
        print(f"[DB ERROR] Query failed: {e}")
        raise
    finally:
        connection.close()


# ============================================================
#  FUNCTION: execute_insert_update()
#  Safe helper for INSERT / UPDATE / DELETE queries.
#  Wraps the operation in a transaction.
#  Commits on success, rolls back on any error.
#  Returns lastrowid so callers know the new record's ID.
# ============================================================
def execute_insert_update(query, params=None):
    """
    Executes an INSERT, UPDATE, or DELETE query.
    Parameters:
        query  (str)   : SQL query string with %s placeholders
        params (tuple) : Values to bind into the placeholders
    Returns:
        int : Last inserted row ID (0 for UPDATE/DELETE)
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            last_id = cursor.lastrowid
        connection.commit()
        return last_id
    except pymysql.MySQLError as e:
        connection.rollback()
        print(f"[DB ERROR] Write operation failed: {e}")
        raise
    finally:
        connection.close()
