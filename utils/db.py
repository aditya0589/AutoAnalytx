import os
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
import streamlit as st

def get_connection_string(db_type, host, port, user, password, database):
    """Constructs the database connection string based on type."""
    if db_type == "MySQL" or db_type == "TiDB":
        return f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    elif db_type == "PostgreSQL":
        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

def create_db_engine(db_type, host, port, user, password, database):
    """Creates and returns a SQLAlchemy engine."""
    connection_string = get_connection_string(db_type, host, port, user, password, database)
    engine = create_engine(connection_string, echo=False)
    return engine

def test_connection(engine):
    """Tests the database connection."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True, "Connection successful!"
    except Exception as e:
        return False, str(e)

def get_tables(engine):
    """Returns a list of table names in the database."""
    inspector = inspect(engine)
    return inspector.get_table_names()

def load_table(engine, table_name, limit=None):
    """Loads a table into a Pandas DataFrame."""
    query = f"SELECT * FROM {table_name}"
    if limit:
        query += f" LIMIT {limit}"
    return pd.read_sql(query, engine)

def get_storage_engine():
    """Creates an engine for the storage database (TiDB) using env vars."""
    user = os.getenv("TIDB_USER", "root")
    password = os.getenv("TIDB_PASSWORD", "")
    host = os.getenv("TIDB_HOST", "127.0.0.1")
    port = os.getenv("TIDB_PORT", "4000")
    database = os.getenv("TIDB_DATABASE", "autoanalytx")
    
    connection_string = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    return create_engine(connection_string, echo=False)

def save_analysis(user_id, query, result_summary, visualization_json=None):
    """Saves an analysis result to the storage database."""
    try:
        engine = get_storage_engine()
        with engine.connect() as connection:
            query_sql = text("""
                INSERT INTO saved_analyses (user_id, query, result_summary, visualization_json)
                VALUES (:user_id, :query, :result_summary, :visualization_json)
            """)
            connection.execute(query_sql, {
                "user_id": user_id,
                "query": query,
                "result_summary": result_summary,
                "visualization_json": visualization_json
            })
            connection.commit()
    except Exception as e:
        st.error(f"Failed to save to storage DB: {e}") 


