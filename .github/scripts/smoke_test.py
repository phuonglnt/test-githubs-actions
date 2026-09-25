"""
.github/scripts/smoke_test.py
Kiểm tra nhanh luồng chính của app bằng Flask test client - không cần trình
duyệt thật. Dùng chung cho cả 2 job CI (sqlite và Postgres) nên bug chỉ xảy
ra ở 1 trong 2 backend (như lỗi GROUP BY từng gặp trên Postgres) sẽ bị bắt.

Không phải bộ test hình thức (không dùng pytest) - chỉ là 1 kịch bản tuần
tự, dừng ngay ở assert đầu tiên sai.
"""

import os
import re
import sys

# Cho phép chạy script này từ bất kỳ đâu (CI gọi bằng đường dẫn tương đối) -
# thêm thư mục gốc repo (2 cấp trên .github/scripts/) vào sys.path để
# "import app" tìm thấy app.py.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import app as flask_app  # noqa: E402


def main():
    client = flask_app.app.test_client()

    r = client.get("/login")
    assert r.status_code == 200, f"GET /login -> {r.status_code}"

    r = client.post("/login", data={"username": "owner", "password": "owner123"})
    assert r.status_code == 302, f"POST /login -> {r.status_code}"

    r = client.get("/")
    assert r.status_code == 200, f"GET / -> {r.status_code}"

    r = client.post(
        "/manage-menu",
        data={"action": "add_dish", "name_dish": "CI Dish", "type": "Plat", "price": "45000"},
    )
    assert r.status_code == 200, f"add_dish -> {r.status_code}"

    r = client.post("/manage-menu", data={"action": "add_table", "seat_count": "4"})
    assert r.status_code == 200, f"add_table -> {r.status_code}"

    r = client.get("/order/1")
    assert r.status_code == 200, f"GET /order/1 -> {r.status_code}"
    menu_id = re.search(rb'data-menu-id="(\d+)"', r.data).group(1).decode()
    bill_id = re.search(rb'data-bill-id="(\d+)"', r.data).group(1).decode()

    r = client.post(f"/api/bill/{bill_id}/add_item", json={"menu_id": menu_id})
    assert r.status_code == 200, f"add_item -> {r.status_code}"

    r = client.post(f"/api/bill/{bill_id}/pay")
    assert r.status_code == 200, f"pay -> {r.status_code}"

    for period in ("day", "week", "month"):
        r = client.get(f"/reports?period={period}")
        assert r.status_code == 200, f"reports?period={period} -> {r.status_code}"

    r = client.post("/staff", data={"action": "add_staff", "username": "ci_staff", "password": "pass123"})
    assert r.status_code == 200, f"add_staff -> {r.status_code}"

    print("Smoke test OK: login, order, pay, reports (day/week/month), staff all passed")


if __name__ == "__main__":
    main()
