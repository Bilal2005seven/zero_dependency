import sqlite3

# Connect to a local database file (or create one if it doesn't exist)
conn = sqlite3.connect("dummy.db")
cursor = conn.cursor()

# Create a simple table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
)
""")

# Insert some dummy data
dummy_users = [
    ("Alice", "alice@example.com"),
    ("Bob", "bob@example.com"),
    ("Charlie", "charlie@example.com")
]

cursor.executemany("INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)", dummy_users)

# Fetch and display all rows
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

print("Dummy Users in DB:")
for row in rows:
    print(row)

# Commit changes and close connection
conn.commit()
conn.close()
