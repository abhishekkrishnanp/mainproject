import sqlite3

conn = sqlite3.connect("career_guidance.db")
cur = conn.cursor()

existing_cols = [c[1] for c in cur.execute("PRAGMA table_info(users)").fetchall()]

cols_to_add = [
    ("user_id", "VARCHAR(100)"),
    ("password_hash", "VARCHAR(255)"),
    ("role", "VARCHAR(50) DEFAULT 'student'"),
    ("updated_at", "DATETIME"),
]

for col_name, col_type in cols_to_add:
    if col_name not in existing_cols:
        cur.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
        print(f"Added column {col_name} to users table")

conn.commit()
conn.close()
print("Database schema migration completed successfully.")
