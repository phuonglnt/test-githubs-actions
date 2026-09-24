"""
setup_db.py
Creates the restaurant.db file and its tables based on the ERD design.
Run this file once to initialize the database.
"""

import sqlite3

DB_NAME = "restaurant.db"


def create_connection():
    """Connect to SQLite and enable foreign key constraints (off by default)."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_tables(conn):
    cursor = conn.cursor()

    # Table_info (restaurant tables)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Table_info (
        Table_number INTEGER PRIMARY KEY AUTOINCREMENT,
        seat_count   INTEGER NOT NULL,
        status       TEXT NOT NULL DEFAULT 'available'
    );
    """)

    # Menu (list of dishes)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Menu (
        ID            INTEGER PRIMARY KEY AUTOINCREMENT,
        name_dish     TEXT NOT NULL,
        type          TEXT,
        price         REAL NOT NULL,
        is_vegetable  INTEGER NOT NULL DEFAULT 0,
        is_active     INTEGER NOT NULL DEFAULT 1
    );
    """)

    # Bill (invoice)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Bill (
        Bill_id     INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_code   TEXT,
        table_id    INTEGER,
        total_bill  REAL DEFAULT 0,
        create_at   TEXT DEFAULT (datetime('now', 'localtime')),
        paid_at     TEXT,
        is_paid     INTEGER NOT NULL DEFAULT 0,
        is_eat_in   INTEGER NOT NULL DEFAULT 1,
        tax         REAL DEFAULT 0,
        FOREIGN KEY (table_id) REFERENCES Table_info(Table_number)
    );
    """)

    # Order_info (line items in a bill)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Order_info (
        Order_id       INTEGER PRIMARY KEY AUTOINCREMENT,
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
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(Menu)")
    existing_columns = [row[1] for row in cursor.fetchall()]

    if "is_active" not in existing_columns:
        cursor.execute("ALTER TABLE Menu ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1")
        conn.commit()
        print("Migrated: added is_active column to Menu")


def migrate_add_bill_code_column(conn):
    """For databases created before bill_code existed: add the column safely."""
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(Bill)")
    existing_columns = [row[1] for row in cursor.fetchall()]

    if "bill_code" not in existing_columns:
        cursor.execute("ALTER TABLE Bill ADD COLUMN bill_code TEXT")
        conn.commit()
        print("Migrated: added bill_code column to Bill")


if __name__ == "__main__":
    conn = create_connection()
    create_tables(conn)
    migrate_add_is_active_column(conn)
    migrate_add_bill_code_column(conn)
    conn.close()
    print(f"Database ready at: {DB_NAME}")
