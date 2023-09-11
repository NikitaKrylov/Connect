import sqlite3


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
                un_state TEXT,
                team TEXT,
                description TEXT,
                isActive INTEGER,
                image TEXT,
                lang TEXT DEFAULT "ru"
            );""")
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author_id INTEGER,
                location TEXT,
                time TEXT, 
                description TEXT,
                invite_link TEXT,
                image TEXT
            );""")

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

    def create_user(self, id: int, name: str, un_state: int, team: str, description: str, isActive: int, image: str, lang: str):
        with self.connection:
            self.cursor.execute("INSERT INTO users (id, name, un_state, team, description, isActive, image, lang) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (id, name, un_state, team, description, isActive, image, lang,))
            return self.cursor.lastrowid

    def get_user(self, _id: int):
        with self.connection:
            return self.cursor.execute("SELECT * FROM users WHERE id = ?", (_id,)).fetchone()

    def update_user_lang(self, _id: int, lang: str):
        with self.connection:
            self.cursor.execute("UPDATE users SET lang=? WHERE id=?", (lang, _id,))

    def change_user_activity(self, _id: int, value: int):
        with self.connection:
            self.cursor.execute("UPDATE users SET isActive=? WHERE id=?", (value, _id,))

    def get_all_users(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM users").fetchall()

    def get_all_active_users(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM users WHERE isActive=1").fetchall()

    def delete_user(self, id: int):
        with self.connection:
            self.cursor.execute("DELETE FROM users WHERE id = ?", (id,))

    def update_user(self, id: int, name: str, un_state: int, team: str, description: str, isActive: int, image: str, lang: str):
        with self.connection:
            return self.cursor.execute("UPDATE users SET name=?, un_state=?, team=?, description=?, isActive=?, image=?, lang=? WHERE id=?", (name, un_state, team, description, isActive, image, lang, id,)).lastrowid

    def create_event(self, id: int, author_id: int, location: str, time: str, description: str, invite_link: str, image: str):
        with self.connection:
            self.cursor.execute("INSERT INTO events (author_id, location, time, description, invite_link, image) VALUES (?, ?, ?, ?, ?, ?)",
                                (author_id, location, time, description, invite_link, image))
            return self.cursor.lastrowid

    def get_all_user_events(self, user_id: int):
        with self.connection:
            return self.cursor.execute("SELECT * FROM events WHERE author_id = ?", (user_id,)).fetchall()

    def event_exists(self, id):
        with self.connection:
            return bool(self.cursor.execute("SELECT * FROM events WHERE id = ?", (id,)).fetchall())

    def get_event(self, _id: int):
        with self.connection:
            return self.cursor.execute("SELECT * FROM events WHERE id = ?", (_id,)).fetchone()

    def delete_event(self, id: int):
        with self.connection:
            self.cursor.execute("DELETE FROM events WHERE id = ?", (id,))

    def get_all_events(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM events").fetchall()

    def get_users_langs(self):
        with self.connection:
            return {_id: lang for _id, lang in self.cursor.execute("SELECT id, lang FROM users").fetchall()}

