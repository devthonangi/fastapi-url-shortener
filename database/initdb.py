import os
import sqlite3

#  Ensure database folder exists
os.makedirs("database", exist_ok=True)

#  Connect to SQLite
conn = sqlite3.connect("database/db.sqlite")
cursor = conn.cursor()

#  Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS short_urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_url TEXT NOT NULL,
    short_key TEXT UNIQUE NOT NULL
);
""")

#  Commit and close
conn.commit()
conn.close()

print(" SQLite database initialized successfully in 'database/db.sqlite'!")
