"""
dbcompat.py
Lớp kết nối DB dùng chung cho sqlite3 (mặc định, chạy local) và PostgreSQL
(khi có biến môi trường DATABASE_URL - dùng khi deploy lên Render, nơi ổ đĩa
bị xoá mỗi lần restart nên không thể dùng file sqlite).

Thiết kế: mọi câu SQL trong models.py / auth.py / các script setup vẫn viết
với dấu "?" làm placeholder và tên cột giữ nguyên hoa/thường (Table_number,
Bill_id, ID, ...) y hệt như trước giờ - module này dịch ngầm sang cú pháp
Postgres, nên KHÔNG cần sửa lại từng câu SQL rải rác khắp nơi:

  - "?"  ->  "%s"                (placeholder Postgres dùng %s, không dùng ?)
  - Kết quả trả về bọc lại thành dict không phân biệt hoa/thường, vì Postgres
    tự hạ tên cột chưa quote về chữ thường (Table_number -> table_number),
    trong khi toàn bộ code/template đang truy cập bằng đúng tên hoa/thường
    gốc (row["Table_number"]).

Muốn lấy id vừa INSERT: dùng insert_returning_id() thay vì cursor.lastrowid
(psycopg2 không có lastrowid - Postgres dùng INSERT ... RETURNING <cột>).
"""

import os

DATABASE_URL = os.environ.get("DATABASE_URL")
IS_POSTGRES = bool(DATABASE_URL)

if IS_POSTGRES:
    import psycopg2
    import psycopg2.extras

    IntegrityError = psycopg2.IntegrityError
else:
    import sqlite3

    IntegrityError = sqlite3.IntegrityError


class _CaseInsensitiveRow(dict):
    """dict thường, chỉ khác: row["Table_number"] và row["table_number"] trỏ
    về cùng 1 giá trị - để bù lại việc Postgres hạ tên cột về chữ thường."""

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            return dict.__getitem__(self, key.lower())

    def __contains__(self, key):
        return dict.__contains__(self, key) or dict.__contains__(self, str(key).lower())


def _wrap_row(row):
    if row is None or not IS_POSTGRES:
        return row
    return _CaseInsensitiveRow(row)


class _CompatCursor:
    """Bọc cursor thật của sqlite3/psycopg2, chỉ lộ ra 4 method mà codebase
    này dùng: execute, fetchone, fetchall, và thuộc tính lastrowid (sqlite)."""

    def __init__(self, real_cursor):
        self._cursor = real_cursor

    def execute(self, query, params=()):
        if IS_POSTGRES:
            query = query.replace("?", "%s")
        self._cursor.execute(query, params)
        return self

    def fetchone(self):
        return _wrap_row(self._cursor.fetchone())

    def fetchall(self):
        return [_wrap_row(r) for r in self._cursor.fetchall()]

    def __getattr__(self, name):
        # Passthrough cho .lastrowid (sqlite), .rowcount, v.v.
        return getattr(self._cursor, name)


def connect(sqlite_path):
    """Mở kết nối DB. Có DATABASE_URL -> luôn dùng Postgres đó cho MỌI bảng
    (bỏ qua sqlite_path - restaurant.db và users.db gộp chung 1 Postgres
    instance, phân biệt bằng tên bảng). Không có -> dùng file sqlite cục bộ
    như trước giờ, không đổi hành vi khi chạy local."""
    if IS_POSTGRES:
        return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    return conn


def cursor(conn):
    return _CompatCursor(conn.cursor())


def insert_returning_id(cur, query, params, pk_column):
    """INSERT rồi trả về id vừa tạo.
    sqlite: cursor.lastrowid. Postgres: không có lastrowid -> thêm RETURNING."""
    if IS_POSTGRES:
        query = query.rstrip().rstrip(";") + f" RETURNING {pk_column}"
        cur.execute(query, params)
        return cur.fetchone()[pk_column]
    cur.execute(query, params)
    return cur.lastrowid


def column_exists(conn, table, column):
    """Dùng trong các hàm migrate_add_*_column - kiểm tra 1 cột đã tồn tại
    chưa trước khi ALTER TABLE, hoạt động trên cả 2 backend."""
    if IS_POSTGRES:
        with conn.cursor() as c:
            c.execute(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_name = %s AND column_name = %s",
                (table.lower(), column.lower()),
            )
            return c.fetchone() is not None
    c = conn.cursor()
    c.execute(f"PRAGMA table_info({table})")
    existing_columns = [row[1] for row in c.fetchall()]
    return column in existing_columns
