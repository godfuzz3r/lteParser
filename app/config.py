import os
import psycopg2
from psycopg2 import pool


def configure(app):
    app.secret_key = os.getenv('FLASK_SECRET_KEY') or 'a286b59c175716fd7a2ab086a7d8b434'

    app.config['DB_HOST'] = os.getenv('DB_HOST') or '127.0.0.1'
    app.config['DB_PORT'] = int(os.getenv('DB_PORT') or 5432)
    app.config['DB_USER'] = os.getenv('POSTGRES_USER') or 'postgres'
    app.config['DB_PASSWORD'] = os.getenv('POSTGRES_PASSWORD') or 'postgres'
    app.config['DATABASE'] = os.getenv('POSTGRES_DB') or 'db'

    app.config['CONN_POOL'] = psycopg2.pool.ThreadedConnectionPool(
        minconn=1,
        maxconn=32,
        host=app.config['DB_HOST'],
        port=app.config['DB_PORT'],
        user = app.config['DB_USER'],
        password=app.config['DB_PASSWORD'],
        database=app.config['DATABASE']
    )

    return app