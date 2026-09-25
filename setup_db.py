"""
setup_db.py
Creates the restaurant.db tables based on the ERD design.
Run this file once to initialize the database.

Local (mặc định): tạo file restaurant.db bằng sqlite3.
Deploy lên Render (có biến môi trường DATABASE_URL): tạo cùng các bảng đó
trong Postgres thay vì sqlite - vì ổ đĩa Render bị xoá mỗi lần service
khởi động lại nên không thể dùng file sqlite ở đó.
"""

import dbcompat

DB_NAME = "restaurant.db"


def create_connection():
    """Kết nối DB và bật ràng buộc khoá ngoại (sqlite tắt mặc định; Postgres
    luôn bật sẵn nên không cần làm gì thêm)."""
    conn = dbcompat.connect(DB_NAME)
    if not dbcompat.IS_POSTGRES:
        conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_tables(conn):
    cursor = conn.cursor()

    if dbcompat.IS_POSTGRES:
        id_type = "SERIAL PRIMARY KEY"
        timestamp_default = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    else:
        id_type = "INTEGER PRIMARY KEY AUTOINCREMENT"
        timestamp_default = "TEXT DEFAULT (datetime('now', 'localtime'))"

    # Table_info (restaurant tables)
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS Table_info (
        Table_number {id_type},
        seat_count   INTEGER NOT NULL,
        status       TEXT NOT NULL DEFAULT 'available'
    );
    """)

    # Menu (list of dishes)
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS Menu (
        ID            {id_type},
        name_dish     TEXT NOT NULL,
        type          TEXT,
        price         REAL NOT NULL,
        is_vegetable  INTEGER NOT NULL DEFAULT 0,
        is_active     INTEGER NOT NULL DEFAULT 1
    );
    """)

    # Bill (invoice)
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS Bill (
        Bill_id     {id_type},
        bill_code   TEXT,
        table_id    INTEGER,
        total_bill  REAL DEFAULT 0,
        create_at   {timestamp_default},
        paid_at     TIMESTAMP,
        is_paid     INTEGER NOT NULL DEFAULT 0,
        is_eat_in   INTEGER NOT NULL DEFAULT 1,
        tax         REAL DEFAULT 0,
        FOREIGN KEY (table_id) REFERENCES Table_info(Table_number)
    );
    """)

    # Order_info (line items in a bill)
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS Order_info (
        Order_id       {id_type},
        bill_id        INTEGER NOT NULL,
        menu_id        INTEGER NOT NULL,
        dish_quantity  INTEGER NOT NULL DEFAULT 1,
        total_dish     REAL NOT NULL,
        FOREIGN KEY (bill_id) REFERENCES Bill(Bill_id),
        FOREIGN KEY (menu_id) REFERENCES Menu(ID)
    );
    """)

    conn.commit()
    print("Created 4 tables: Table_info, Menu, Bill, Order_info")


def migrate_add_is_active_column(conn):
    """For databases created before is_active existed: add the column safely."""
    if not dbcompat.column_exists(conn, "Menu", "is_active"):
        conn.cursor().execute("ALTER TABLE Menu ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1")
        conn.commit()
        print("Migrated: added is_active column to Menu")


def migrate_add_bill_code_column(conn):
    """For databases created before bill_code existed: add the column safely."""
    if not dbcompat.column_exists(conn, "Bill", "bill_code"):
        conn.cursor().execute("ALTER TABLE Bill ADD COLUMN bill_code TEXT")
        conn.commit()
        print("Migrated: added bill_code column to Bill")


if __name__ == "__main__":
    conn = create_connection()
    create_tables(conn)
    migrate_add_is_active_column(conn)
    migrate_add_bill_code_column(conn)
    conn.close()
    print(f"Database ready ({'Postgres' if dbcompat.IS_POSTGRES else DB_NAME}).")
