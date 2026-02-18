"""
Database module for URL Shortener
Handles SQLite operations with thread-safe connections
"""
import sqlite3
import threading
from contextlib import contextmanager
from typing import Optional

class Database:
    def __init__(self, db_path: str = "urls.db"):
        self.db_path = db_path
        self._local = threading.local()
        self._init_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection"""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False
            )
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
    
    def _init_db(self):
        """Initialize database schema"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    short_code TEXT UNIQUE NOT NULL,
                    original_url TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    clicks INTEGER DEFAULT 0
                )
            """)
            
            # Create index for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_short_code ON urls(short_code)
            """)
    
    def create_url(self, short_code: str, original_url: str) -> bool:
        """
        Create a new URL mapping
        Returns True if successful, False if short_code already exists
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(
                    "INSERT INTO urls (short_code, original_url) VALUES (?, ?)",
                    (short_code, original_url)
                )
                return True
        except sqlite3.IntegrityError:
            # Short code already exists
            return False
    
    def get_url(self, short_code: str) -> Optional[dict]:
        """
        Get original URL by short code
        Also increments the click counter
        Returns dict with url data or None if not found
        """
        with self.get_cursor() as cursor:
            # Get the URL
            cursor.execute(
                "SELECT * FROM urls WHERE short_code = ?",
                (short_code,)
            )
            row = cursor.fetchone()
            
            if row:
                # Increment click counter
                cursor.execute(
                    "UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?",
                    (short_code,)
                )
                return dict(row)
            return None
    
    def url_exists(self, short_code: str) -> bool:
        """Check if a short code already exists"""
        with self.get_cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM urls WHERE short_code = ?",
                (short_code,)
            )
            return cursor.fetchone() is not None
    
    def get_all_urls(self, limit: int = 100) -> list:
        """Get all URLs (for admin/debugging)"""
        with self.get_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM urls ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

# Global database instance
db = Database()