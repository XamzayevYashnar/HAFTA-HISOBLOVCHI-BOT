import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('database.sqlite', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            username TEXT NULL,
            podpiska BOOLEAN DEFAULT 0
        )
        """)
        self.conn.commit()

    def add_user(self, user_id, username):
        self.cursor.execute(
            """INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)""",
            (user_id, username)
        )
        self.conn.commit()

    def get_user(self, user_id):
        self.cursor.execute("""SELECT * FROM users WHERE user_id = ?""", (user_id,))
        return self.cursor.fetchone()

    def update_podpiska(self, user_id, status: bool):
        """подписка ustunini yangilash"""
        self.cursor.execute(
            "UPDATE users SET podpiska = ? WHERE user_id = ?",
            (status, user_id)
        )
        self.conn.commit()
