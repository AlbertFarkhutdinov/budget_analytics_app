"""The module provides function for creating database."""
import sqlalchemy as sql

from backend.entries_app.settings import DBSettings

db_settings = DBSettings()


def create_postgres_database() -> None:
    """
    Create a PostgreSQL database if it does not already exist.

    This function connects to the PostgreSQL server using a temporary engine,
    checks whether the specified database exists, and creates it if necessary.

    """
    temp_engine = sql.create_engine(
        sql.URL.create(
            drivername='postgresql',
            username=db_settings.db_user,
            password=db_settings.db_password,
            host=db_settings.db_host,
            port=db_settings.db_port,
            database='postgres',
        ),
    )
    with temp_engine.connect() as conn:
        conn.execute(sql.text('COMMIT'))
        sql_query = sql.text(
            """
            DO $$ BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_database WHERE datname = :db_name
                ) THEN
                    EXECUTE format('CREATE DATABASE %I', :db_name);
                END IF;
            END $$;
            """,
        )
        conn.execute(
            sql_query,
            parameters={
                'db_name': db_settings.db_name,
            },
        )
    temp_engine.dispose()


def get_engine() -> sql.Engine:
    """
    Create and return a SQLAlchemy engine for the application's database.

    Returns
    -------
    sqlalchemy.Engine
        SQLAlchemy engine connected to the specified database.

    """
    return sql.create_engine(
        sql.URL.create(
            drivername='postgresql',
            username=db_settings.db_user,
            password=db_settings.db_password,
            host=db_settings.db_host,
            port=db_settings.db_port,
            database=db_settings.db_name,
        ),
    )
