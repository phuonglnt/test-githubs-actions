"""
app.py
Flask backend cho hệ thống order nhà hàng, có đăng nhập + phân quyền
(owner / staff) dùng users.db riêng biệt.
"""

from datetime import date, datetime, timedelta
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from models import MenuManager, TableManager, BillManager, ReportManager
from auth import (
    find_user_by_username, verify_password, create_staff_account,
    get_all_staff, update_staff_account, update_avatar_color,
    update_user_currency, update_user_language, AVATAR_COLORS, CURRENCIES,
    login_required, owner_required,
)
from translations import (
    t as translate, weekday_name, month_name,
    LANGUAGES, LANGUAGE_NAMES,
)

app = Flask(__name__)
app.secret_key = "doi-chuoi-nay-thanh-random-that-truoc-khi-dung-that"  # đổi khi deploy thật

# Prices are always stored in the database as plain VND numbers. Currency
# choice only changes how they're DISPLAYED - approximate fixed rates, not
# live exchange rates (fine for an in-house tool, not for real FX accuracy).
CURRENCY_RATES_FROM_VND = {"VND": 1, "USD": 1 / 25000, "EUR": 1 / 27000}
CURRENCY_SYMBOLS = {"VND": "đ", "USD": "$", "EUR": "€"}
CURRENCY_DECIMALS = {"VND": 0, "USD": 2, "EUR": 2}


def format_money(amount_vnd):
    currency = session.get("currency", "VND")
    converted = (amount_vnd or 0) * CURRENCY_RATES_FROM_VND.get(currency, 1)
    decimals = CURRENCY_DECIMALS.get(currency, 0)
    symbol = CURRENCY_SYMBOLS.get(currency, "đ")
    formatted_number = f"{converted:,.{decimals}f}"
    return f"{formatted_number} {symbol}" if currency == "VND" else f"{symbol}{formatted_number}"


def get_dish_categories(dishes):
    """Distinct, non-empty dish types, for the category filter tabs on the order screen."""
    seen = []
    for d in dishes:
        cat = (d["type"] or "").strip()
        if cat and cat not in seen:
            seen.append(cat)
    return seen


# Gợi ý nhóm món hiện trong ô nhập (datalist) - vẫn gõ tự do được giá trị khác.
DISH_CATEGORY_SUGGESTIONS = ["Entrée", "Plat", "Boisson", "Dessert", "Accompagnement"]


def parse_price(raw):
    """Form price -> float >= 0, or None if blank / not a number / negative."""
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    return value if value >= 0 else None


def parse_seat_count(raw):
    """Form seat count -> int >= 1, or None if blank / not an integer / < 1."""
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return None
    return value if value >= 1 else None


def current_language():
    """The UI language for this request - stored on the session at login and
    changed via the picker in the avatar dropdown. Defaults to English."""
    return session.get("language", "en")


def t(key):
    """Translate a key into the current session language (for use inside routes)."""
    return translate(key, current_language())


@app.context_processor
def inject_globals():
    return {
        "avatar_colors": AVATAR_COLORS,
        "currencies": CURRENCIES,
        "current_currency": session.get("currency", "VND"),
        "format_money": format_money,
        "languages": LANGUAGES,
        "language_names": LANGUAGE_NAMES,
        "current_language": current_language(),
        "t": t,
    }


def format_date_with_weekday(d):
    """e.g. 'Monday 07/09/2026' - weekday name follows the current UI language."""
    return f"{weekday_name(d.weekday(), current_language())} {d.strftime('%d/%m/%Y')}"


# ---------- Đăng nhập / Đăng xuất ----------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = find_user_by_username(username)
        if user is None or not verify_password(user, password):
            return render_template("login.html", error=t("err_bad_login"))

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]
        session["avatar_color"] = user["avatar_color"]
        session["currency"] = user["currency"]
        session["language"] = user["language"]
        return redirect(url_for("table_map"))

    return render_template("login.html", error=None)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------- Avatar ----------

@app.route("/api/profile/avatar", methods=["POST"])
@login_required
def change_avatar():
    color = request.get_json().get("color")
    if color not in AVATAR_COLORS:
        return jsonify({"error": t("err_invalid_color")}), 400

    update_avatar_color(session["user_id"], color)
    session["avatar_color"] = color
    return jsonify({"avatar_color": color})


@app.route("/api/profile/currency", methods=["POST"])
@login_required
def change_currency():
    currency = request.get_json().get("currency")
    if currency not in CURRENCIES:
        return jsonify({"error": t("err_invalid_currency")}), 400

    update_user_currency(session["user_id"], currency)
    session["currency"] = currency
    return jsonify({"currency": currency})


@app.route("/api/profile/language", methods=["POST"])
@login_required
def change_language():
    language = request.get_json().get("language")
    if language not in LANGUAGES:
        return jsonify({"error": t("err_invalid_language")}), 400

    update_user_language(session["user_id"], language)
    session["language"] = language
    return jsonify({"language": language})


# ---------- Quản lý nhân viên (chỉ chủ) ----------

@app.route("/staff", methods=["GET", "POST"])
@login_required
@owner_required
def staff_management():
    error = None
    if request.method == "POST":
        action = request.form.get("action", "add_staff")

        if action == "edit_staff":
            user_id = request.form.get("user_id")
            username = request.form.get("username", "").strip()
            new_password = request.form.get("new_password", "").strip()
            if not username:
                error = t("err_username_empty")
            else:
                success, message = update_staff_account(user_id, username, new_password or None)
                if not success:
                    error = t(message)
        else:
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            if not username or not password:
                error = t("err_fill_user_pass")
            else:
                success, message = create_staff_account(username, password)
                if not success:
                    error = t(message)

    staff_list = get_all_staff()
    return render_template("staff.html", staff_list=staff_list, error=error)


# ---------- Menu & table management (owner only) ----------

@app.route("/manage-menu", methods=["GET", "POST"])
@login_required
@owner_required
def manage_menu():
    error = None
    if request.method == "POST":
        action = request.form.get("action")
        menu_mgr = MenuManager()

        if action == "add_dish":
            name_dish = request.form.get("name_dish", "").strip()
            price = request.form.get("price", "")
            type_ = request.form.get("type", "").strip()
            is_vegetable = 1 if request.form.get("is_vegetable") == "on" else 0

            price_value = parse_price(price)
            if not name_dish or not price:
                error = t("err_fill_dish")
            elif price_value is None:
                error = t("err_price_invalid")
            else:
                menu_mgr.add_menu_item(name_dish, type_, price_value, is_vegetable)

        elif action == "edit_dish":
            menu_id = request.form.get("menu_id")
            name_dish = request.form.get("name_dish", "").strip()
            price = request.form.get("price", "")
            type_ = request.form.get("type", "").strip()
            is_vegetable = 1 if request.form.get("is_vegetable") == "on" else 0

            price_value = parse_price(price)
            if not name_dish or not price:
                error = t("err_fill_dish")
            elif price_value is None:
                error = t("err_price_invalid")
            else:
                menu_mgr.update_menu_item(menu_id, name_dish, type_, price_value, is_vegetable)

        elif action == "deactivate_dish":
            menu_id = request.form.get("menu_id")
            menu_mgr.set_menu_item_active(menu_id, is_active=False)

        elif action == "reactivate_dish":
            menu_id = request.form.get("menu_id")
            menu_mgr.set_menu_item_active(menu_id, is_active=True)

        menu_mgr.close()

        if action == "add_table":
            seat_count = request.form.get("seat_count", "")
            seats_value = parse_seat_count(seat_count)
            if not seat_count:
                error = t("err_fill_seats")
            elif seats_value is None:
                error = t("err_seats_invalid")
            else:
                table_mgr = TableManager()
                table_mgr.add_table(seats_value)
                table_mgr.close()

        elif action == "edit_table":
            table_id = request.form.get("table_id")
            seat_count = request.form.get("seat_count", "")
            seats_value = parse_seat_count(seat_count)
            if not seat_count:
                error = t("err_fill_seats")
            elif seats_value is None:
                error = t("err_seats_invalid")
            else:
                table_mgr = TableManager()
                table_mgr.update_table(table_id, seats_value)
                table_mgr.close()

        elif action == "delete_table":
            table_id = request.form.get("table_id")
            table_mgr = TableManager()
            success, message = table_mgr.delete_table(table_id)
            table_mgr.close()
            if not success:
                error = t(message)

    menu_mgr = MenuManager()
    all_dishes = menu_mgr.get_all_menu_items()
    menu_mgr.close()

    table_mgr = TableManager()
    all_tables = table_mgr.get_tables()
    table_mgr.close()

    return render_template(
        "manage_menu.html",
        dishes=all_dishes,
        tables=all_tables,
        error=error,
        category_suggestions=DISH_CATEGORY_SUGGESTIONS,
    )


# ---------- Sales report (both owner and staff can view) ----------

@app.route("/reports")
@login_required
def reports():
    period = request.args.get("period", "day")
    date_param = request.args.get("date")

    if date_param:
        selected_date = datetime.strptime(date_param, "%Y-%m-%d").date()
    else:
        selected_date = date.today()

    if period == "week":
        start_date = selected_date - timedelta(days=selected_date.weekday())  # Monday
        end_date = start_date + timedelta(days=6)  # Sunday
        date_label = f"{format_date_with_weekday(start_date)} - {format_date_with_weekday(end_date)}"
    elif period == "month":
        start_date = selected_date.replace(day=1)
        if start_date.month == 12:
            next_month = start_date.replace(year=start_date.year + 1, month=1)
        else:
            next_month = start_date.replace(month=start_date.month + 1)
        end_date = next_month - timedelta(days=1)
        date_label = f"{month_name(start_date.month, current_language())} {start_date.year}"
    else:
        period = "day"
        start_date = end_date = selected_date
        date_label = format_date_with_weekday(selected_date)

    report_mgr = ReportManager()
    bills = report_mgr.get_bills_by_date_range(start_date.isoformat(), end_date.isoformat())
    report_mgr.close()

    bill_mgr = BillManager()
    dine_in_bills = []
    takeaway_bills = []

    for b in bills:
        bill_data = {
            "bill_id": b["Bill_id"],
            "bill_code": b["bill_code"],
            "paid_at": b["paid_at"],
            "total_bill": b["total_bill"],
            "line_items": bill_mgr.get_bill_details(b["Bill_id"]),
        }
        if b["is_eat_in"]:
            dine_in_bills.append(bill_data)
        else:
            takeaway_bills.append(bill_data)
    bill_mgr.close()

    dine_in_total = sum(b["total_bill"] for b in dine_in_bills)
    takeaway_total = sum(b["total_bill"] for b in takeaway_bills)
    grand_total = dine_in_total + takeaway_total

    return render_template(
        "reports.html",
        period=period,
        selected_date=selected_date.isoformat(),
        date_label=date_label,
        dine_in_bills=dine_in_bills,
        takeaway_bills=takeaway_bills,
        dine_in_total=dine_in_total,
        takeaway_total=takeaway_total,
        grand_total=grand_total,
    )


# ---------- Sơ đồ bàn / Order (đã có, giờ thêm login_required) ----------

@app.route("/")
@login_required
def table_map():
    table_mgr = TableManager()
    tables = table_mgr.get_tables()
    table_mgr.close()
    return render_template("table_map.html", tables=tables)


@app.route("/order/<int:table_id>")
@login_required
def order_screen(table_id):
    bill_mgr = BillManager()
    existing_bill_id = bill_mgr.get_open_bill_for_table(table_id)
    if existing_bill_id is not None:
        bill_id = existing_bill_id
    else:
        bill_id = bill_mgr.create_bill(table_id=table_id, is_eat_in=1, tax=0.1)

    items = bill_mgr.get_bill_details(bill_id)
    total = bill_mgr.calculate_total_bill(bill_id)
    bill_code = bill_mgr.get_bill(bill_id)["bill_code"]
    bill_mgr.close()

    menu_mgr = MenuManager()
    dishes = menu_mgr.get_menu()
    menu_mgr.close()

    return render_template(
        "order.html",
        table_id=table_id,
        bill_id=bill_id,
        bill_code=bill_code,
        dishes=dishes,
        dish_categories=get_dish_categories(dishes),
        items=items,
        total=total,
    )


@app.route("/takeaway/new", methods=["POST"])
@login_required
def new_takeaway_order():
    """Start a new takeaway order - it isn't tied to any table, and is paid
    right away in the same flow rather than sitting open like a dine-in bill."""
    bill_mgr = BillManager()
    bill_id = bill_mgr.create_bill(table_id=None, is_eat_in=0, tax=0.1)
    bill_mgr.close()
    return redirect(url_for("order_screen_takeaway", bill_id=bill_id))


@app.route("/order/takeaway/<int:bill_id>")
@login_required
def order_screen_takeaway(bill_id):
    bill_mgr = BillManager()
    items = bill_mgr.get_bill_details(bill_id)
    total = bill_mgr.calculate_total_bill(bill_id)
    bill_code = bill_mgr.get_bill(bill_id)["bill_code"]
    bill_mgr.close()

    menu_mgr = MenuManager()
    dishes = menu_mgr.get_menu()
    menu_mgr.close()

    return render_template(
        "order.html",
        table_id=None,
        bill_id=bill_id,
        bill_code=bill_code,
        dishes=dishes,
        dish_categories=get_dish_categories(dishes),
        items=items,
        total=total,
    )


@app.route("/api/bill/<int:bill_id>/add_item", methods=["POST"])
@login_required
def add_item(bill_id):
    data = request.get_json()
    menu_id = data.get("menu_id")

    bill_mgr = BillManager()
    bill_mgr.add_item_to_bill(bill_id, menu_id, 1)
    items = bill_mgr.get_bill_details(bill_id)
    total = bill_mgr.calculate_total_bill(bill_id)
    bill_mgr.close()

    return jsonify({
        "items": [
            {
                "name_dish": r["name_dish"],
                "dish_quantity": r["dish_quantity"],
                "total_dish_formatted": format_money(r["total_dish"]),
            }
            for r in items
        ],
        "total_formatted": format_money(total),
    })


@app.route("/api/bill/<int:bill_id>/pay", methods=["POST"])
@login_required
def pay_bill(bill_id):
    bill_mgr = BillManager()
    items = bill_mgr.get_bill_details(bill_id)
    if not items:
        bill_mgr.close()
        return jsonify({"error": t("err_bill_empty")}), 400

    total = bill_mgr.close_bill(bill_id)
    bill_mgr.close()
    return jsonify({"total_formatted": format_money(total)})


if __name__ == "__main__":
    app.run(debug=True)
