"""
setup_users_db.py
Tạo bảng Users (đăng nhập), tách hoàn toàn khỏi restaurant.db. Chạy 1 lần để
khởi tạo. Tự động seed sẵn đúng 1 tài khoản chủ (role = 'owner') nếu chưa có
tài khoản chủ nào.

Local (mặc định): lưu vào file users.db bằng sqlite3.
Deploy lên Render (có biến môi trường DATABASE_URL): dùng Postgres thay vì
sqlite, vì ổ đĩa Render bị xoá mỗi lần service khởi động lại.
"""

import os

import dbcompat
from werkzeug.security import generate_password_hash

USERS_DB = "users.db"

# Đọc từ biến môi trường OWNER_USERNAME / OWNER_PASSWORD nếu có (đặt trong
# Render: Environment -> Add Environment Variable) - để KHÔNG BAO GIỜ phải
# hardcode mật khẩu thật vào file này rồi commit lên GitHub. Không set thì
# rơi về mặc định owner/owner123 như cũ, chạy local không đổi gì.
DEFAULT_OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "owner")
DEFAULT_OWNER_PASSWORD = os.environ.get("OWNER_PASSWORD", "owner123")  # đổi ngay sau khi bàn giao thật


def create_users_table():
    conn = dbcompat.connect(USERS_DB)
    id_type = "SERIAL PRIMARY KEY" if dbcompat.IS_POSTGRES else "INTEGER PRIMARY KEY AUTOINCREMENT"
    created_default = (
        "TIMESTAMP DEFAULT CURRENT_TIMESTAMP" if dbcompat.IS_POSTGRES
        else "TEXT DEFAULT (datetime('now', 'localtime'))"
    )
    conn.cursor().execute(f"""
        CREATE TABLE IF NOT EXISTS Users (
            id            {id_type},
            username      TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role          TEXT NOT NULL CHECK(role IN ('owner', 'staff')),
            avatar_color  TEXT NOT NULL DEFAULT '#4361EE',
            currency      TEXT NOT NULL DEFAULT 'VND',
            language      TEXT NOT NULL DEFAULT 'en',
            created_at    {created_default}
        );
    """)
    conn.commit()
    return conn


def migrate_add_columns(conn):
    """For users.db created before currency / language existed: add the columns safely."""
    if not dbcompat.column_exists(conn, "Users", "currency"):
        conn.cursor().execute("ALTER TABLE Users ADD COLUMN currency TEXT NOT NULL DEFAULT 'VND'")
        conn.commit()
        print("Migrated: added currency column to Users")

    if not dbcompat.column_exists(conn, "Users", "language"):
        conn.cursor().execute("ALTER TABLE Users ADD COLUMN language TEXT NOT NULL DEFAULT 'en'")
        conn.commit()
        print("Migrated: added language column to Users")


def seed_owner_account(conn):
    cursor = dbcompat.cursor(conn)
    cursor.execute("SELECT COUNT(*) AS cnt FROM Users WHERE role = 'owner'")
    owner_count = cursor.fetchone()["cnt"]

    if owner_count > 0:
        print("Owner account already exists, skipping creation.")
        return

    cursor.execute(
        "INSERT INTO Users (username, password_hash, role) VALUES (?, ?, 'owner')",
        (DEFAULT_OWNER_USERNAME, generate_password_hash(DEFAULT_OWNER_PASSWORD, method="pbkdf2:sha256"))
    )
    conn.commit()
    password_source = "OWNER_PASSWORD env var" if os.environ.get("OWNER_PASSWORD") else "built-in default (owner123)"
    print(f"Default owner account created -> username: {DEFAULT_OWNER_USERNAME} | password from: {password_source}")
    print("NOTE: there is no in-app password change feature yet. To change it, edit the DB directly.")


if __name__ == "__main__":
    conn = create_users_table()
    migrate_add_columns(conn)
    seed_owner_account(conn)
    conn.close()
    print(f"Users table ready ({'Postgres' if dbcompat.IS_POSTGRES else USERS_DB}).")
