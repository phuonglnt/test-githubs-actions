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

    # Bill (invoice). table_id KHÔNG có ràng buộc khoá ngoại tới Table_info
    # (cố ý, xem migrate_drop_table_fk) - chủ quán muốn xoá được 1 bàn dù
    # bàn đó đã có hoá đơn gắn vào; hoá đơn cũ vẫn giữ nguyên table_id cũ,
    # chỉ là số đó có thể không còn trỏ tới bàn nào đang tồn tại nữa.
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
        tax         REAL DEFAULT 0
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


def migrate_drop_table_fk(conn):
    """Bill.table_id từng có FOREIGN KEY tới Table_info(Table_number), khiến
    không xoá được 1 bàn nếu nó đã có hoá đơn gắn vào. Bỏ ràng buộc đó đi -
    hoá đơn cũ vẫn giữ nguyên table_id, chỉ là số đó có thể không còn trỏ
    tới bàn nào đang tồn tại nữa (chấp nhận được, đổi lại xoá bàn tự do)."""
    if dbcompat.IS_POSTGRES:
        conn.cursor().execute("ALTER TABLE Bill DROP CONSTRAINT IF EXISTS bill_table_id_fkey")
        conn.commit()
        print("Migrated: dropped Bill.table_id foreign key (Postgres)")
        return

    cursor = conn.cursor()
    fks = cursor.execute("PRAGMA foreign_key_list(Bill)").fetchall()
    still_has_fk = any(row[2] == "Table_info" for row in fks)  # row[2] = bảng được tham chiếu
    if not still_has_fk:
        return

    # SQLite không có ALTER TABLE ... DROP CONSTRAINT - phải tạo lại bảng
    # không có FK rồi copy dữ liệu qua, đúng quy trình chuẩn của SQLite.
    conn.execute("PRAGMA foreign_keys = OFF")
    cursor.execute("""
        CREATE TABLE Bill_new (
            Bill_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_code   TEXT,
            table_id    INTEGER,
            total_bill  REAL DEFAULT 0,
            create_at   TEXT DEFAULT (datetime('now', 'localtime')),
            paid_at     TIMESTAMP,
            is_paid     INTEGER NOT NULL DEFAULT 0,
            is_eat_in   INTEGER NOT NULL DEFAULT 1,
            tax         REAL DEFAULT 0
        )
    """)
    cursor.execute("""
        INSERT INTO Bill_new (Bill_id, bill_code, table_id, total_bill, create_at, paid_at, is_paid, is_eat_in, tax)
        SELECT Bill_id, bill_code, table_id, total_bill, create_at, paid_at, is_paid, is_eat_in, tax FROM Bill
    """)
    cursor.execute("DROP TABLE Bill")
    cursor.execute("ALTER TABLE Bill_new RENAME TO Bill")
    conn.commit()
    conn.execute("PRAGMA foreign_keys = ON")
    print("Migrated: dropped Bill.table_id foreign key (sqlite, table rebuilt)")


if __name__ == "__main__":
    conn = create_connection()
    create_tables(conn)
    migrate_add_is_active_column(conn)
    migrate_add_bill_code_column(conn)
    migrate_drop_table_fk(conn)
    conn.close()
    print(f"Database ready ({'Postgres' if dbcompat.IS_POSTGRES else DB_NAME}).")
