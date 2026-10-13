"""
Expense Tracker - Automated Test Suite
=======================================
All tests use an isolated temporary SQLite database.
The production database is never touched during testing.

Run with:
    python -m pytest test_app.py -v
"""

import os
import tempfile
import pytest

# ── Import the application ─────────────────────────────────────────────────────
import app as expense_app


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def client(tmp_path):
    """
    Create a fresh Flask test client backed by a temporary SQLite database.
    The database is created fresh for every test function.
    """
    # Point the application at a temp DB path
    test_db = str(tmp_path / "test_expenses.db")
    expense_app.DB_PATH = test_db
    expense_app.DATA_DIR = str(tmp_path)

    expense_app.app.config["TESTING"] = True
    expense_app.app.config["WTF_CSRF_ENABLED"] = False

    # Initialise the schema
    expense_app.init_db()

    with expense_app.app.test_client() as c:
        yield c


@pytest.fixture
def seeded_client(client, tmp_path):
    """
    A test client that already has one expense and one budget record.
    Uses the `client` fixture so the DB is always isolated.
    """
    import sqlite3
    conn = sqlite3.connect(expense_app.DB_PATH)
    conn.execute(
        """INSERT INTO expenses
           (title, amount, category, expense_date, payment_method, description)
           VALUES (?, ?, ?, ?, ?, ?)""",
        ("Seed Expense", 250.0, "Food", "2024-01-15", "Cash", "Seeded for tests")
    )
    conn.execute(
        "INSERT INTO budgets (monthly_budget) VALUES (?)", (5000.0,)
    )
    conn.commit()
    conn.close()
    return client


# ── Test 1: Flask app initialises successfully ─────────────────────────────────

def test_app_initialises(client):
    assert expense_app.app is not None
    assert expense_app.app.config["TESTING"] is True


# ── Test 2: Home dashboard returns HTTP 200 ────────────────────────────────────

def test_dashboard_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


# ── Test 3: Add Expense page returns HTTP 200 ──────────────────────────────────

def test_add_expense_page_returns_200(client):
    response = client.get("/add")
    assert response.status_code == 200


# ── Test 4: An expense can be created ─────────────────────────────────────────

def test_create_expense(client):
    response = client.post("/add_expense", data={
        "title": "Lunch",
        "amount": "120.50",
        "category": "Food",
        "expense_date": "2024-03-01",
        "payment_method": "UPI",
        "description": "Office canteen lunch",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Lunch" in response.data or b"successfully" in response.data.lower()


# ── Test 5: Created expense is stored in SQLite ────────────────────────────────

def test_expense_stored_in_db(client):
    import sqlite3
    client.post("/add_expense", data={
        "title": "Grocery Shopping",
        "amount": "850",
        "category": "Shopping",
        "expense_date": "2024-03-10",
        "payment_method": "Debit Card",
        "description": "Weekend groceries",
    })
    conn = sqlite3.connect(expense_app.DB_PATH)
    row = conn.execute(
        "SELECT * FROM expenses WHERE title = ?", ("Grocery Shopping",)
    ).fetchone()
    conn.close()
    assert row is not None
    assert row[2] == 850.0        # amount column


# ── Test 6: Expense history displays stored records ────────────────────────────

def test_expense_history_displays_records(seeded_client):
    response = seeded_client.get("/expenses")
    assert response.status_code == 200
    assert b"Seed Expense" in response.data


# ── Test 7: Expense search and filtering work ──────────────────────────────────

def test_expense_search(seeded_client):
    response = seeded_client.get("/expenses?search=Seed")
    assert response.status_code == 200
    assert b"Seed Expense" in response.data

def test_expense_category_filter(seeded_client):
    response = seeded_client.get("/expenses?category=Food")
    assert response.status_code == 200
    assert b"Seed Expense" in response.data

def test_expense_month_filter(seeded_client):
    response = seeded_client.get("/expenses?month=2024-01")
    assert response.status_code == 200
    assert b"Seed Expense" in response.data


# ── Test 8: An existing expense can be edited ──────────────────────────────────

def test_edit_expense(seeded_client):
    import sqlite3
    # Get the ID of the seeded expense
    conn = sqlite3.connect(expense_app.DB_PATH)
    row = conn.execute("SELECT id FROM expenses LIMIT 1").fetchone()
    conn.close()
    expense_id = row[0]

    # Edit form should load
    response = seeded_client.get(f"/edit/{expense_id}")
    assert response.status_code == 200

    # Submit update
    response = seeded_client.post(f"/update/{expense_id}", data={
        "title": "Updated Expense",
        "amount": "300",
        "category": "Food",
        "expense_date": "2024-01-15",
        "payment_method": "Cash",
        "description": "Updated description",
    }, follow_redirects=True)
    assert response.status_code == 200

    # Verify in DB
    conn = sqlite3.connect(expense_app.DB_PATH)
    updated = conn.execute(
        "SELECT title, amount FROM expenses WHERE id = ?", (expense_id,)
    ).fetchone()
    conn.close()
    assert updated[0] == "Updated Expense"
    assert updated[1] == 300.0


# ── Test 9: An expense can be deleted via POST ─────────────────────────────────

def test_delete_expense(seeded_client):
    import sqlite3
    conn = sqlite3.connect(expense_app.DB_PATH)
    row = conn.execute("SELECT id FROM expenses LIMIT 1").fetchone()
    conn.close()
    expense_id = row[0]

    response = seeded_client.post(f"/delete/{expense_id}", follow_redirects=True)
    assert response.status_code == 200

    conn = sqlite3.connect(expense_app.DB_PATH)
    deleted = conn.execute(
        "SELECT id FROM expenses WHERE id = ?", (expense_id,)
    ).fetchone()
    conn.close()
    assert deleted is None


# ── Test 10: Invalid expense amounts are rejected ──────────────────────────────

def test_invalid_amount_rejected(client):
    response = client.post("/add_expense", data={
        "title": "Bad Entry",
        "amount": "not-a-number",
        "category": "Food",
        "expense_date": "2024-03-01",
        "payment_method": "Cash",
    }, follow_redirects=True)
    assert response.status_code == 200
    import sqlite3
    conn = sqlite3.connect(expense_app.DB_PATH)
    row = conn.execute(
        "SELECT id FROM expenses WHERE title = ?", ("Bad Entry",)
    ).fetchone()
    conn.close()
    assert row is None  # Must NOT be stored

def test_negative_amount_rejected(client):
    response = client.post("/add_expense", data={
        "title": "Negative Entry",
        "amount": "-50",
        "category": "Food",
        "expense_date": "2024-03-01",
        "payment_method": "Cash",
    }, follow_redirects=True)
    assert response.status_code == 200
    import sqlite3
    conn = sqlite3.connect(expense_app.DB_PATH)
    row = conn.execute(
        "SELECT id FROM expenses WHERE title = ?", ("Negative Entry",)
    ).fetchone()
    conn.close()
    assert row is None

def test_zero_amount_rejected(client):
    response = client.post("/add_expense", data={
        "title": "Zero Entry",
        "amount": "0",
        "category": "Food",
        "expense_date": "2024-03-01",
        "payment_method": "Cash",
    }, follow_redirects=True)
    assert response.status_code == 200
    import sqlite3
    conn = sqlite3.connect(expense_app.DB_PATH)
    row = conn.execute(
        "SELECT id FROM expenses WHERE title = ?", ("Zero Entry",)
    ).fetchone()
    conn.close()
    assert row is None


# ── Test 11: Budget can be created or updated ──────────────────────────────────

def test_budget_set(client):
    response = client.post("/update_budget", data={
        "monthly_budget": "10000"
    }, follow_redirects=True)
    assert response.status_code == 200
    budget = expense_app.get_budget()
    assert budget == 10000.0

def test_budget_update(seeded_client):
    seeded_client.post("/update_budget", data={"monthly_budget": "20000"})
    budget = expense_app.get_budget()
    assert budget == 20000.0


# ── Test 12: Dashboard totals are calculated from DB records ───────────────────

def test_dashboard_totals_from_db(seeded_client):
    stats = expense_app.get_dashboard_stats()
    assert stats["tx_count"] == 1
    assert stats["total_all"] == 250.0
    assert stats["budget"] == 5000.0


# ── Test 13: Reports return expected results ───────────────────────────────────

def test_reports_page(seeded_client):
    response = seeded_client.get("/reports")
    assert response.status_code == 200
    assert b"Food" in response.data

def test_reports_with_empty_db(client):
    """Reports must work even with no expense records."""
    response = client.get("/reports")
    assert response.status_code == 200


# ── Test 14: Invalid expense IDs are handled safely ───────────────────────────

def test_invalid_expense_id_edit(client):
    response = client.get("/edit/999999", follow_redirects=True)
    assert response.status_code == 200  # Must not raise 500

def test_invalid_expense_id_update(client):
    response = client.post("/update/999999", data={
        "title": "Ghost",
        "amount": "100",
        "category": "Food",
        "expense_date": "2024-01-01",
        "payment_method": "Cash",
    }, follow_redirects=True)
    assert response.status_code == 200

def test_invalid_expense_id_delete(client):
    response = client.post("/delete/999999", follow_redirects=True)
    assert response.status_code == 200


# ── Test 15: Application works with an initially empty database ────────────────

def test_empty_database_dashboard(client):
    """Dashboard must work when no expenses or budgets exist."""
    response = client.get("/")
    assert response.status_code == 200

def test_empty_database_expenses(client):
    response = client.get("/expenses")
    assert response.status_code == 200

def test_empty_database_budget(client):
    response = client.get("/budget")
    assert response.status_code == 200

def test_empty_database_reports(client):
    response = client.get("/reports")
    assert response.status_code == 200

def test_dashboard_zero_budget_no_division_error(client):
    """Must not raise ZeroDivisionError when budget is 0."""
    stats = expense_app.get_dashboard_stats()
    assert stats["budget"] == 0.0
    assert stats["pct"] == 0.0
    assert stats["remaining"] == 0.0
