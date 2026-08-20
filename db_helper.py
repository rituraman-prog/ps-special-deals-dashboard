"""
Database Helper - Works with both SQLite (local) and PostgreSQL (cloud)
"""

import os
import sqlite3
from urllib.parse import urlparse


def get_db_connection():
    """
    Get database connection - automatically uses PostgreSQL if DATABASE_URL exists,
    otherwise falls back to SQLite
    """
    database_url = os.environ.get('DATABASE_URL')

    if database_url:
        # Cloud deployment - use PostgreSQL
        return get_postgres_connection(database_url)
    else:
        # Local deployment - use SQLite
        return get_sqlite_connection()


def get_sqlite_connection():
    """Get SQLite connection (local)"""
    conn = sqlite3.connect('data/opportunities.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_postgres_connection(database_url):
    """Get PostgreSQL connection (cloud)"""
    import psycopg2
    from psycopg2.extras import RealDictCursor

    # Parse the database URL
    result = urlparse(database_url)

    conn = psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )

    # Use RealDictCursor for dict-like access (similar to sqlite3.Row)
    conn.row_factory = RealDictCursor

    return conn


def init_database():
    """Initialize database tables (works for both SQLite and PostgreSQL)"""
    database_url = os.environ.get('DATABASE_URL')

    if database_url:
        init_postgres_database(database_url)
    else:
        init_sqlite_database()


def init_sqlite_database():
    """Initialize SQLite database"""
    import sqlite3

    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)

    conn = sqlite3.connect('data/opportunities.db')
    cursor = conn.cursor()

    # Create opportunities table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS opportunities (
            id TEXT PRIMARY KEY,
            name TEXT,
            account_name TEXT,
            amount REAL,
            close_date TEXT,
            stage_name TEXT,
            owner_name TEXT,
            opportunity_type TEXT,
            created_date TEXT,
            last_modified_date TEXT,
            upload_date TEXT,
            upload_filename TEXT,
            project_manager TEXT,
            project_manager_2 TEXT,
            opportunity_owner TEXT,
            region TEXT,
            subregion TEXT,
            special_term TEXT,
            billing_frequency TEXT,
            account_number TEXT,
            amount_currency TEXT,
            opportunity_stage TEXT,
            billings_currency TEXT,
            billings REAL,
            actual_remaining_currency TEXT,
            actual_remaining REAL,
            invoiced_currency TEXT,
            invoiced REAL,
            po_number TEXT,
            exclude_from_billing INTEGER
        )
    ''')

    # Create upload history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS upload_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            upload_date TEXT,
            records_count INTEGER,
            status TEXT
        )
    ''')

    conn.commit()
    conn.close()


def init_postgres_database(database_url):
    """Initialize PostgreSQL database"""
    import psycopg2
    from urllib.parse import urlparse

    result = urlparse(database_url)

    conn = psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )

    cursor = conn.cursor()

    # Create opportunities table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS opportunities (
            id TEXT PRIMARY KEY,
            name TEXT,
            account_name TEXT,
            amount REAL,
            close_date TEXT,
            stage_name TEXT,
            owner_name TEXT,
            opportunity_type TEXT,
            created_date TEXT,
            last_modified_date TEXT,
            upload_date TEXT,
            upload_filename TEXT,
            project_manager TEXT,
            project_manager_2 TEXT,
            opportunity_owner TEXT,
            region TEXT,
            subregion TEXT,
            special_term TEXT,
            billing_frequency TEXT,
            account_number TEXT,
            amount_currency TEXT,
            opportunity_stage TEXT,
            billings_currency TEXT,
            billings REAL,
            actual_remaining_currency TEXT,
            actual_remaining REAL,
            invoiced_currency TEXT,
            invoiced REAL,
            po_number TEXT,
            exclude_from_billing INTEGER
        )
    ''')

    # Create upload history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS upload_history (
            id SERIAL PRIMARY KEY,
            filename TEXT,
            upload_date TEXT,
            records_count INTEGER,
            status TEXT
        )
    ''')

    conn.commit()
    conn.close()
