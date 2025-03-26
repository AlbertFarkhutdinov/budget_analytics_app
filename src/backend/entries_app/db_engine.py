import sqlalchemy as sql

from backend.entries_app.settings import DBSettings

db_settings = DBSettings()


def create_postgres_database() -> None:
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
