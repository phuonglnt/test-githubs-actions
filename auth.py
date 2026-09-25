"""
auth.py
Xử lý đăng nhập, phân quyền (owner / staff), và quản lý avatar.
Dùng file users.db riêng biệt, tách hoàn toàn khỏi restaurant.db.
"""

from functools import wraps
from flask import session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

import dbcompat

USERS_DB = "users.db"

# 7 màu cầu vồng (đỏ - cam - vàng - lục - lam - chàm - tím).
# Avatar hiển thị chữ trắng nên các sắc đã chọn đủ đậm để đọc rõ.
AVATAR_COLORS = [
    "#E03131",  # đỏ
    "#F76707",  # cam
    "#F0A500",  # vàng
    "#2F9E44",  # lục
    "#1C7ED6",  # lam
    "#3B5BDB",  # chàm
    "#9C36B5",  # tím
]

CURRENCIES = ["VND", "USD", "EUR"]


def get_connection():
    return dbcompat.connect(USERS_DB)


def find_user_by_username(username):
    conn = get_connection()
    cur = dbcompat.cursor(conn)
    cur.execute("SELECT * FROM Users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row


def find_user_by_id(user_id):
    conn = get_connection()
    cur = dbcompat.cursor(conn)
    cur.execute("SELECT * FROM Users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row


def verify_password(user_row, password):
    return check_password_hash(user_row["password_hash"], password)


def create_staff_account(username, password):
    """Create a new staff account. Returns (success: bool, error message or None)."""
    conn = get_connection()
    try:
        cur = dbcompat.cursor(conn)
        cur.execute(
            "INSERT INTO Users (username, password_hash, role) VALUES (?, ?, 'staff')",
            (username, generate_password_hash(password, method="pbkdf2:sha256"))
        )
        conn.commit()
        return True, None
    except dbcompat.IntegrityError:
        return False, "err_username_taken"
    finally:
        conn.close()


def get_all_staff():
    conn = get_connection()
    cur = dbcompat.cursor(conn)
    cur.execute("SELECT * FROM Users WHERE role = 'staff' ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows


def update_staff_account(user_id, username, new_password=None):
    """Edit a staff account's username, and optionally reset their password
    (leave new_password empty/None to keep the current password unchanged)."""
    conn = get_connection()
    try:
        cur = dbcompat.cursor(conn)
        if new_password:
            cur.execute(
                "UPDATE Users SET username = ?, password_hash = ? WHERE id = ? AND role = 'staff'",
                (username, generate_password_hash(new_password, method="pbkdf2:sha256"), user_id)
            )
        else:
            cur.execute(
                "UPDATE Users SET username = ? WHERE id = ? AND role = 'staff'",
                (username, user_id)
            )
        conn.commit()
        return True, None
    except dbcompat.IntegrityError:
        return False, "err_username_taken"
    finally:
        conn.close()


def update_avatar_color(user_id, color):
    conn = get_connection()
    dbcompat.cursor(conn).execute("UPDATE Users SET avatar_color = ? WHERE id = ?", (color, user_id))
    conn.commit()
    conn.close()


def update_user_currency(user_id, currency):
    conn = get_connection()
    dbcompat.cursor(conn).execute("UPDATE Users SET currency = ? WHERE id = ?", (currency, user_id))
    conn.commit()
    conn.close()


def update_user_language(user_id, language):
    conn = get_connection()
    dbcompat.cursor(conn).execute("UPDATE Users SET language = ? WHERE id = ?", (language, user_id))
    conn.commit()
    conn.close()


# ---------- Decorator kiểm tra đăng nhập / phân quyền ----------

def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped


def owner_required(view_func):
    """Chỉ tài khoản role='owner' mới vào được. Nhân viên bị đá về màn sơ đồ bàn."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if session.get("role") != "owner":
            return redirect(url_for("table_map"))
        return view_func(*args, **kwargs)
    return wrapped
