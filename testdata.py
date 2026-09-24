"""
test_data.py
Insert dữ liệu mẫu + test các câu SELECT/JOIN sẽ dùng trong app thật.
Chạy sau khi đã chạy setup_db.py.
"""

import sqlite3
from setup_db import create_connection


def insert_sample_data(conn):
    cursor = conn.cursor()

    # --- Bàn ăn ---
    cursor.execute("INSERT INTO Table_info (seat_count, status) VALUES (4, 'in_use')")
    table1_id = cursor.lastrowid  # bàn số 1

    cursor.execute("INSERT INTO Table_info (seat_count, status) VALUES (6, 'available')")

    # --- Menu ---
    cursor.execute("INSERT INTO Menu (name_dish, type, price, is_vegetable) VALUES (?, ?, ?, ?)",
                    ("Phở bò", "món chính", 45000, 0))
    pho_id = cursor.lastrowid

    cursor.execute("INSERT INTO Menu (name_dish, type, price, is_vegetable) VALUES (?, ?, ?, ?)",
                    ("Rau muống xào", "món phụ", 25000, 1))
    rau_id = cursor.lastrowid

    cursor.execute("INSERT INTO Menu (name_dish, type, price, is_vegetable) VALUES (?, ?, ?, ?)",
                    ("Trà đá", "nước uống", 5000, 1))
    tra_id = cursor.lastrowid

    # --- Bill: 1 đơn ăn tại bàn (table_id có giá trị) ---
    cursor.execute("""
        INSERT INTO Bill (table_id, is_eat_in, tax) VALUES (?, 1, 0.1)
    """, (table1_id,))
    bill_eat_in_id = cursor.lastrowid

    # --- Bill: 1 đơn mang về (table_id = NULL) ---
    cursor.execute("""
        INSERT INTO Bill (table_id, is_eat_in, tax) VALUES (NULL, 0, 0.1)
    """)
    bill_takeaway_id = cursor.lastrowid

    # --- Order_info cho đơn ăn tại bàn: 2 phở + 1 rau muống ---
    cursor.execute("""
        INSERT INTO Order_info (bill_id, menu_id, dish_quantity, total_dish)
        VALUES (?, ?, ?, ?)
    """, (bill_eat_in_id, pho_id, 2, 45000 * 2))

    cursor.execute("""
        INSERT INTO Order_info (bill_id, menu_id, dish_quantity, total_dish)
        VALUES (?, ?, ?, ?)
    """, (bill_eat_in_id, rau_id, 1, 25000 * 1))

    # --- Order_info cho đơn mang về: 1 phở + 2 trà đá ---
    cursor.execute("""
        INSERT INTO Order_info (bill_id, menu_id, dish_quantity, total_dish)
        VALUES (?, ?, ?, ?)
    """, (bill_takeaway_id, pho_id, 1, 45000 * 1))

    cursor.execute("""
        INSERT INTO Order_info (bill_id, menu_id, dish_quantity, total_dish)
        VALUES (?, ?, ?, ?)
    """, (bill_takeaway_id, tra_id, 2, 5000 * 2))

    conn.commit()
    print("Đã insert dữ liệu mẫu: 2 bàn, 3 món, 2 hoá đơn (1 tại bàn + 1 mang về)")
    return bill_eat_in_id, bill_takeaway_id


def test_queries(conn, bill_id):
    cursor = conn.cursor()

    print("\n=== 1. Xem chi tiết 1 hoá đơn: tên món + số lượng + giá ===")
    cursor.execute("""
        SELECT Menu.name_dish, Order_info.dish_quantity, Order_info.total_dish
        FROM Order_info
        JOIN Menu ON Order_info.menu_id = Menu.ID
        WHERE Order_info.bill_id = ?
    """, (bill_id,))
    for row in cursor.fetchall():
        print(f"  {row[0]:<20} x{row[1]:<3} = {row[2]:,.0f} đ")

    print("\n=== 2. Tính tổng tiền 1 hoá đơn (đã cộng thuế) ===")
    cursor.execute("""
        SELECT SUM(Order_info.total_dish), Bill.tax
        FROM Order_info
        JOIN Bill ON Order_info.bill_id = Bill.Bill_id
        WHERE Bill.Bill_id = ?
    """, (bill_id,))
    subtotal, tax = cursor.fetchone()
    total = subtotal * (1 + tax)
    print(f"  Tạm tính: {subtotal:,.0f} đ | Thuế: {tax*100:.0f}% | Tổng: {total:,.0f} đ")

    print("\n=== 3. Thống kê món bán chạy nhất (theo tổng số lượng) ===")
    cursor.execute("""
        SELECT Menu.name_dish, SUM(Order_info.dish_quantity) AS total_qty
        FROM Order_info
        JOIN Menu ON Order_info.menu_id = Menu.ID
        GROUP BY Menu.name_dish
        ORDER BY total_qty DESC
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]:<20} : {row[1]} phần")

    print("\n=== 4. Kiểm tra đơn mang về (table_id phải là NULL) ===")
    cursor.execute("""
        SELECT Bill_id, table_id, is_eat_in
        FROM Bill
        WHERE is_eat_in = 0
    """)
    for row in cursor.fetchall():
        print(f"  Bill_id={row[0]} | table_id={row[1]} | is_eat_in={row[2]}")


if __name__ == "__main__":
    conn = create_connection()
    bill_eat_in_id, bill_takeaway_id = insert_sample_data(conn)
    test_queries(conn, bill_eat_in_id)
    conn.close()