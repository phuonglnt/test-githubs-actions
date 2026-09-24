"""
reset_and_start.py
Deletes restaurant.db and users.db completely, recreates both from scratch
(empty tables, fresh default owner account), then starts the Flask app.

Use this when you want to wipe ALL data (tables, menu, bills, staff accounts)
and start over with a clean slate.

Run:
    python3 reset_and_start.py
"""

import os
import subprocess
import sys

DB_FILES = ["restaurant.db", "users.db"]


def delete_existing_databases():
    for db_file in DB_FILES:
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"Deleted {db_file}")
        else:
            print(f"{db_file} did not exist, nothing to delete")


def run_step(description, script_name):
    print(f"\n--- {description} ---")
    subprocess.run([sys.executable, script_name], check=True)


def main():
    print("Resetting the restaurant system to a clean, empty state...")
    delete_existing_databases()

    run_step("Recreating restaurant.db", "setup_db.py")
    run_step("Recreating users.db and default owner account", "setup_users_db.py")

    print("\nAll data has been reset. Starting the app...\n")
    subprocess.run([sys.executable, "app.py"], check=True)


if __name__ == "__main__":
    main()
