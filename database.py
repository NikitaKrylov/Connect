import sqlite3
from sqlite3 import Cursor
from datetime import datetime

class Database:
    connection = None
    cursor = None
    _db_name = "db.db"
    def __init__(self, *args, **kwargs):
        self._create()

    def _create(self):
        self._connect()
        with self.connection:
            self.cursor.execute("PRAGMA foreign_keys = ON")
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                age INTEGER,
                group TEXT,
                description TEXT,
                isActive INTEGER
            );""")
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time_start TEXT, 
                time_end TEXT, 
                description TEXT
            );""")
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS images (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            path TEXT, 
                            time_end TEXT, 
                            description TEXT
                        );""")


            return self

    def _connect(self):
        try:
            self.connection = sqlite3.connect(self._db_name)
            self.cursor = self.connection.cursor()
        except Exception as exc:
            print(f"error {exc}")

    def close(self):
        self.connection.close()

    def user_exists(self, id):
        with self.connection:
            return bool(self.cursor.execute("SELECT * FROM users WHERE id = ?", (id,)).fetchall())
    def event_exists(self, id):
        with self.connection:
            return bool(self.cursor.execute("SELECT * FROM events WHERE id = ?", (id,)).fetchall())

    def create_user(self, id: int, name: str, age: int, group: str, description: str, isActive: int):
        with self.connection:
            self.cursor.execute("INSERT INTO users (id, name, age, group, description, isActive) VALUES (?, ?, ?, ?, ?, ?)",
                                (id, name, age, group, description, isActive))
            return self.cursor.lastrowid

    def create_event(self, time_start: str, time_end: str, description: str):
        with self.connection:
            self.cursor.execute("INSERT INTO events (time_start, time_end, description) VALUES (?, ?, ?)",
                                (time_start, time_end, description))
            return self.cursor.lastrowid


