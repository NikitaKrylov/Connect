import sqlite3
from sqlite3 import Cursor
from datetime import datetime
from models import UserData, EventData, ImageData

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
                teem TEXT,
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
                            path TEXT
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
    def image_exists(self, id):
        with self.connection:
            return bool(self.cursor.execute("SELECT * FROM images WHERE id = ?", (id,)).fetchall())

    def create_user(self, id: int, name: str, age: int, teem: str, description: str, isActive: int):
        with self.connection:
            self.cursor.execute("INSERT INTO users (id, name, age, teem, description, isActive) VALUES (?, ?, ?, ?, ?, ?)",
                                (id, name, age, teem, description, isActive))
            return self.cursor.lastrowid

    def create_event(self, time_start: str, time_end: str, description: str):
        with self.connection:
            self.cursor.execute("INSERT INTO events (time_start, time_end, description) VALUES (?, ?, ?)",
                                (time_start, time_end, description))
            return self.cursor.lastrowid

    def create_image(self, path: str):
        with self.connection:
            self.cursor.execute("INSERT INTO images (path) VALUES (?)",
                                (path,))
            return self.cursor.lastrowid

    def delete_user(self, id: int):
        with self.connection:
            self.cursor.execute("DELETE FROM users WHERE id = ?", (id,))

    def delete_event(self, id: int):
        with self.connection:
            self.cursor.execute("DELETE FROM events WHERE id = ?", (id,))

    def delete_image(self, id: int):
        with self.connection:
            self.cursor.execute("DELETE FROM images WHERE id = ?", (id,))

    def get_all_users(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM users").fetchall()
    def get_all_users_dc(self):
        with self.connection:
            return [UserData(*i) for i in self.cursor.execute("SELECT * FROM users").fetchall()]
    def get_all_events(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM events").fetchall()
    def get_all_events_dc(self):
        with self.connection:
            return [EventData(*i) for i in self.cursor.execute("SELECT * FROM events").fetchall()]
    def get_all_images(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM images").fetchall()
    def get_all_images_dc(self):
        with self.connection:
            return [ImageData(*i) for i in self.cursor.execute("SELECT * FROM images").fetchall()]
