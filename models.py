import sqlite3
from datetime import datetime

DB_NAME = 'restaurant.db'

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.conn.execute("PRAGMA foreign_keys = 1")
        self.conn.row_factory = sqlite3.Row

        self.cursor = self.conn.cursor()
    
    def close(self):
        self.conn.close()

class MenuManager(Database):
    def add_menu_item(self, name_dish, type_, price, is_vegetable=0):
        self.cursor.execute(
            "INSERT INTO Menu (name_dish, type, price, is_vegetable) VALUES (?, ?, ?, ?)",
            (name_dish, type_, price, is_vegetable)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def get_menu(self):
        """Dishes shown to customers when ordering - active dishes only."""
        self.cursor.execute("SELECT * FROM Menu WHERE is_active = 1")
        return self.cursor.fetchall()

    def get_all_menu_items(self):
        """All dishes including deactivated ones - used on the owner's menu management page."""
        self.cursor.execute("SELECT * FROM Menu ORDER BY ID")
        return self.cursor.fetchall()

    def get_dish_menu(self, menu_id):
        self.cursor.execute("SELECT * FROM Menu WHERE id = ?", (menu_id,))
        return self.cursor.fetchone()

    def update_menu_item(self, menu_id, name_dish, type_, price, is_vegetable):
        self.cursor.execute(
            "UPDATE Menu SET name_dish = ?, type = ?, price = ?, is_vegetable = ? WHERE ID = ?",
            (name_dish, type_, price, is_vegetable, menu_id)
        )
        self.conn.commit()

    def set_menu_item_active(self, menu_id, is_active):
        """Soft delete / restore a dish. We never hard-delete a dish that may
        already be referenced by past orders - hiding it keeps old bills intact."""
        self.cursor.execute(
            "UPDATE Menu SET is_active = ? WHERE ID = ?", (1 if is_active else 0, menu_id)
        )
        self.conn.commit()

class TableManager(Database):
    def add_table(self, seat_count, status='available'):
        self.cursor.execute(
            "INSERT INTO Table_info (seat_count, status) VALUES (?, ?)",
            (seat_count, status)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def get_tables(self):
        self.cursor.execute("SELECT * FROM Table_info")
        return self.cursor.fetchall()

    def change_table_status(self, table_id, new_status):
        # FIX 1: id -> Table_number
        self.cursor.execute("UPDATE Table_info SET status = ? WHERE Table_number = ?", (new_status, table_id))
        self.conn.commit()

    def update_table(self, table_id, seat_count):
        self.cursor.execute(
            "UPDATE Table_info SET seat_count = ? WHERE Table_number = ?", (seat_count, table_id)
        )
        self.conn.commit()

    def delete_table(self, table_id):
        """Hard-delete a table. Blocked if the table already has bill history,
        since Bill.table_id references it - deleting would break past records."""
        try:
            self.cursor.execute("DELETE FROM Table_info WHERE Table_number = ?", (table_id,))
            self.conn.commit()
            return True, None
        except sqlite3.IntegrityError:
            return False, "err_table_has_history"

class BillManager(Database):
    def create_bill(self, table_id=None, is_eat_in=1, tax=0.1):
        now = datetime.now()

        # Count how many bills already exist today to get this bill's order number of the day
        today_str = now.strftime("%Y-%m-%d")
        self.cursor.execute("SELECT COUNT(*) FROM Bill WHERE DATE(create_at) = ?", (today_str,))
        order_number_today = self.cursor.fetchone()[0] + 1

        # Prefix EI (eat-in) or TA (takeaway) so bill codes are distinguishable at a glance
        bill_type_prefix = "EI" if is_eat_in else "TA"

        # Format: EI-HHMM-DDMMYYYY-NN or TA-HHMM-DDMMYYYY-NN
        bill_code = f"{bill_type_prefix}-{now.strftime('%H%M')}-{now.strftime('%d%m%Y')}-{order_number_today:02d}"

        self.cursor.execute(
            "INSERT INTO Bill (bill_code, table_id, is_eat_in, tax) VALUES (?, ?, ?, ?)",
            (bill_code, table_id, is_eat_in, tax)
        )
        self.conn.commit()
        bill_id = self.cursor.lastrowid

        if table_id is not None:
            self.cursor.execute("UPDATE Table_info SET status = 'in_use' WHERE table_number = ?", (table_id,))
            self.conn.commit()
        return bill_id

    def add_item_to_bill(self, bill_id, menu_id, dish_quantity):
        self.cursor.execute("SELECT price FROM Menu WHERE id = ?", (menu_id,))
        row = self.cursor.fetchone()
        if row is None:
            raise ValueError("Menu item not found")
        price = row['price']

        # If this dish is already on the bill, increase its quantity instead of
        # adding a duplicate line (so "Coca Cola" clicked 3 times shows as one
        # line: Coca Cola x3, not three separate x1 lines).
        self.cursor.execute(
            "SELECT Order_id, dish_quantity FROM Order_info WHERE bill_id = ? AND menu_id = ?",
            (bill_id, menu_id)
        )
        existing = self.cursor.fetchone()

        if existing:
            new_quantity = existing["dish_quantity"] + dish_quantity
            self.cursor.execute(
                "UPDATE Order_info SET dish_quantity = ?, total_dish = ? WHERE Order_id = ?",
                (new_quantity, price * new_quantity, existing["Order_id"])
            )
        else:
            self.cursor.execute(
                "INSERT INTO Order_info (bill_id, menu_id, dish_quantity, total_dish) VALUES (?, ?, ?, ?)",
                (bill_id, menu_id, dish_quantity, price * dish_quantity)
            )
        self.conn.commit()

    def get_open_bill_for_table(self, table_id):
        """Find the UNPAID bill for a table (if it currently has an order in progress)."""
        self.cursor.execute(
            "SELECT Bill_id FROM Bill WHERE table_id = ? AND is_paid = 0 ORDER BY Bill_id DESC LIMIT 1",
            (table_id,)
        )
        row = self.cursor.fetchone()
        return row["Bill_id"] if row else None

    def get_bill(self, bill_id):
        self.cursor.execute("SELECT * FROM Bill WHERE Bill_id = ?", (bill_id,))
        return self.cursor.fetchone()

    def get_bill_details(self, bill_id):
        self.cursor.execute("""
            SELECT Menu.name_dish, SUM(Order_info.dish_quantity) AS dish_quantity, SUM(Order_info.total_dish) AS total_dish
            FROM Order_info
            JOIN Menu ON Order_info.menu_id = Menu.ID
            WHERE Order_info.bill_id = ?
            GROUP BY Order_info.menu_id
            ORDER BY MIN(Order_info.Order_id)
        """, (bill_id,))
        return self.cursor.fetchall()

    def calculate_total_bill(self, bill_id):
        # Get tax directly from Bill (kept separate from Order_info so it
        # doesn't come back NULL when the bill has no items yet - a JOIN
        # would return zero rows if Order_info has nothing for this bill)
        self.cursor.execute("SELECT tax FROM Bill WHERE Bill_id = ?", (bill_id,))
        bill_row = self.cursor.fetchone()
        tax = bill_row["tax"] if bill_row else 0

        self.cursor.execute(
            "SELECT SUM(total_dish) FROM Order_info WHERE bill_id = ?", (bill_id,)
        )
        subtotal = self.cursor.fetchone()[0] or 0

        return subtotal * (1 + tax)

    def close_bill(self, bill_id):
        total = self.calculate_total_bill(bill_id)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""UPDATE Bill SET is_paid =1, paid_at = ?, total_bill = ? WHERE Bill_id = ?""", (now, total, bill_id))
        self.conn.commit()

        self.cursor.execute("SELECT table_id FROM Bill WHERE Bill_id = ?", (bill_id,))
        row = self.cursor.fetchone()
        if row["table_id"] is not None:
            self.cursor.execute(
                "UPDATE Table_info SET status = 'available' WHERE Table_number = ?",
                (row["table_id"],)
            )
            self.conn.commit()
 
        return total

# FIX 3: moved ReportManager out to top level, no longer nested inside BillManager
class ReportManager(Database):
    # FIX 4: renamed the method + added GROUP BY
    def get_top_selling_dishes(self, top_n=5):
        self.cursor.execute("""
            SELECT Menu.name_dish, SUM(Order_info.dish_quantity) AS total_qty
            FROM Order_info
            JOIN Menu ON Order_info.menu_id = Menu.ID
            GROUP BY Menu.name_dish
            ORDER BY total_qty DESC
            LIMIT ?
            """, (top_n,))
        return self.cursor.fetchall()

    def report_total_sales_daily(self):
        self.cursor.execute("""
            SELECT DATE(Bill.paid_at) AS sale_date, SUM(Bill.total_bill) AS total_sales
            FROM Bill
            WHERE Bill.is_paid = 1
            GROUP BY sale_date
            ORDER BY sale_date DESC
        """)
        return self.cursor.fetchall()

    def get_bills_by_date_range(self, start_date, end_date):
        """All PAID bills whose paid_at date falls within [start_date, end_date] (inclusive)."""
        self.cursor.execute("""
            SELECT * FROM Bill
            WHERE is_paid = 1 AND DATE(paid_at) BETWEEN ? AND ?
            ORDER BY paid_at DESC
        """, (start_date, end_date))
        return self.cursor.fetchall()
