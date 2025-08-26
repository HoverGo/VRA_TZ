# src/core/dependencies/db_dependency.py
import sqlite3
from contextlib import contextmanager

from src.core.config import settings


class DBManager:
    def __init__(self, db_url: str = settings.DB_URL):
        self.db_url = db_url
        self.init_db()

    @contextmanager
    def get_conn(self):
        conn = sqlite3.connect(self.db_url)
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            conn.commit()

db_manager = DBManager(settings.DB_URL)