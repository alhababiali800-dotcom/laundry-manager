import sqlite3
import os
from contextlib import contextmanager
from pathlib import Path

# Store DB in user's AppData (Windows) or home dir
def get_db_path():
    if os.name == 'nt':
        base = Path(os.environ.get('APPDATA', Path.home())) / 'InternationalLaundries'
    else:
        base = Path.home() / '.international_laundries'
    base.mkdir(parents=True, exist_ok=True)
    return str(base / 'laundry.db')

DB_PATH = get_db_path()

class Database:
    _conn = None
    _transaction_depth = 0

    @classmethod
    def get(cls):
        if cls._conn is None:
            cls._conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            cls._conn.row_factory = sqlite3.Row
            cls._conn.execute("PRAGMA journal_mode=WAL")
            cls._conn.execute("PRAGMA foreign_keys=ON")
        return cls._conn

    @classmethod
    def execute(cls, query, params=()):
        conn = cls.get()
        cur = conn.cursor()
        cur.execute(query, params)
        if cls._transaction_depth == 0:
            conn.commit()
        return cur

    @classmethod
    @contextmanager
    def transaction(cls):
        """Run related writes atomically and roll them back on failure."""
        conn = cls.get()
        if cls._transaction_depth:
            cls._transaction_depth += 1
            try:
                yield conn
            finally:
                cls._transaction_depth -= 1
            return
        conn.execute("BEGIN IMMEDIATE")
        cls._transaction_depth = 1
        try:
            yield conn
        except Exception:
            conn.rollback()
            raise
        else:
            conn.commit()
        finally:
            cls._transaction_depth = 0

    @classmethod
    def fetchall(cls, query, params=()):
        cur = cls.execute(query, params)
        return [dict(r) for r in cur.fetchall()]

    @classmethod
    def fetchone(cls, query, params=()):
        cur = cls.execute(query, params)
        row = cur.fetchone()
        return dict(row) if row else None

    @classmethod
    def lastrowid(cls, query, params=()):
        cur = cls.execute(query, params)
        return cur.lastrowid
