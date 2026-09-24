"""
setup_users_db.py
Tạo file users.db riêng biệt (KHÔNG chung với restaurant.db) để chứa tài khoản
đăng nhập. Chạy 1 lần để khởi tạo. Tự động seed sẵn đúng 1 tài khoản chủ
(role = 'owner') nếu chưa có tài khoản chủ nào.
"""

import sqlite3
from werkzeug.security import generate_password_hash

USERS_DB = "users.db"

DEFAULT_OWNER_USERNAME = "owner"
DEFAULT_OWNER_PASSWORD = "owner123"  # đổi ngay sau khi bàn giao thật


def create_users_table():
    conn = sqlite3.connect(USERS_DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role          TEXT NOT NULL CHECK(role IN ('owner', 'staff')),
            avatar_color  TEXT NOT NULL DEFAULT '#4361EE',
            currency      TEXT NOT NULL DEFAULT 'VND',
            language      TEXT NOT NULL DEFAULT 'en',
            created_at    TEXT DEFAULT (datetime('now', 'localtime'))
        );
    """)
    conn.commit()
    return conn


def migrate_add_columns(conn):
    """For users.db created before currency / language existed: add the columns safely."""
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(Users)")
    existing_columns = [row[1] for row in cursor.fetchall()]

    if "currency" not in existing_columns:
        cursor.execute("ALTER TABLE Users ADD COLUMN currency TEXT NOT NULL DEFAULT 'VND'")
        conn.commit()
        print("Migrated: added currency column to Users")

    if "language" not in existing_columns:
        cursor.execute("ALTER TABLE Users ADD COLUMN language TEXT NOT NULL DEFAULT 'en'")
        conn.commit()
        print("Migrated: added language column to Users")


def seed_owner_account(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Users WHERE role = 'owner'")
    owner_count = cursor.fetchone()[0]

    if owner_count > 0:
        print("Owner account already exists, skipping creation.")
        return

    cursor.execute(
        "INSERT INTO Users (username, password_hash, role) VALUES (?, ?, 'owner')",
        (DEFAULT_OWNER_USERNAME, generate_password_hash(DEFAULT_OWNER_PASSWORD, method="pbkdf2:sha256"))
    )
    conn.commit()
    print(f"Default owner account created -> username: {DEFAULT_OWNER_USERNAME} | password: {DEFAULT_OWNER_PASSWORD}")
    print("NOTE: there is no in-app password change feature yet. To change it, edit users.db directly.")


if __name__ == "__main__":
    conn = create_users_table()
    migrate_add_columns(conn)
    seed_owner_account(conn)
    conn.close()
    print("users.db is ready.")
