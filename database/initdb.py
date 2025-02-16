import os
import sqlite3

#  Ensure database folder exists
DB_FOLDER = "database"
DB_FILE = f"{DB_FOLDER}/db.sqlite"

os.makedirs(DB_FOLDER, exist_ok=True)

#  Connect to SQLite
try:
    conn = sqlite3.connect(DB_FILE)
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
    print(f"✅ SQLite database initialized successfully in '{DB_FILE}'!")

except sqlite3.Error as e:
    print(f"❌ Database initialization failed: {e}")

finally:
    if conn:
        conn.close()
