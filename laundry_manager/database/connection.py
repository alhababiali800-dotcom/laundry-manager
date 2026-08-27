import sqlite3
import os
from contextlib import contextmanager
from pathlib import Path
import threading

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
    _lock = threading.Lock()  # Thread safety for concurrent access
    _cache = {}  # Simple query result cache
    _cache_ttl = {}  # Cache time-to-live tracking
    _cache_lock = threading.Lock()

    @classmethod
    def get(cls):
        if cls._conn is None:
            # Use check_same_thread=True for better safety, handle threading explicitly
            cls._conn = sqlite3.connect(DB_PATH, check_same_thread=True, timeout=10.0)
            cls._conn.row_factory = sqlite3.Row
            cls._conn.execute("PRAGMA journal_mode=WAL")
            cls._conn.execute("PRAGMA foreign_keys=ON")
            cls._conn.execute("PRAGMA synchronous=NORMAL")  # Better performance without sacrificing safety
        return cls._conn

    @classmethod
    def execute(cls, query, params=()):
        with cls._lock:
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
        with cls._lock:
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
    def fetchall(cls, query, params=(), use_cache=False, cache_key=None):
        # Check cache if enabled
        if use_cache and cache_key:
            with cls._cache_lock:
                if cache_key in cls._cache:
                    return cls._cache[cache_key]
        
        cur = cls.execute(query, params)
        result = [dict(r) for r in cur.fetchall()]
        
        # Store in cache if enabled
        if use_cache and cache_key:
            with cls._cache_lock:
                cls._cache[cache_key] = result
        
        return result

    @classmethod
    def fetchone(cls, query, params=()):
        cur = cls.execute(query, params)
        row = cur.fetchone()
        return dict(row) if row else None

    @classmethod
    def lastrowid(cls, query, params=()):
        cur = cls.execute(query, params)
        return cur.lastrowid
    
    @classmethod
    def clear_cache(cls, cache_key=None):
        """Clear specific cache entry or all cache."""
        with cls._cache_lock:
            if cache_key:
                cls._cache.pop(cache_key, None)
                cls._cache_ttl.pop(cache_key, None)
            else:
                cls._cache.clear()
                cls._cache_ttl.clear()
