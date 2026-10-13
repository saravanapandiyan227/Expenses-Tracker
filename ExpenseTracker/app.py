"""
Expense Tracker - Flask Backend
================================
A simple, single-user expense tracking web application built with Flask and SQLite.

NOTE: This is a college-level DevOps demonstration project.
It is NOT a multi-user financial platform and must NOT be used for
sensitive financial information without additional security controls.
"""

import os
import sqlite3
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "expense-tracker-dev-secret-2024")

# ─── Database Configuration ────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "expenses.db")

CATEGORIES = [
    "Food", "Transportation", "Shopping", "Bills and Utilities",
    "Healthcare", "Education", "Entertainment", "Travel", "Rent", "Other"
]

PAYMENT_METHODS = [
    "Cash", "UPI", "Debit Card", "Credit Card", "Bank Transfer", "Other"
]

BUDGET_WARNING_THRESHOLD = 0.80  # Warn when 80% of budget is spent


# ─── Database Helpers ──────────────────────────────────────────────────────────

def get_db():
    """Return a new SQLite connection with row_factory set."""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create tables if they do not already exist. Never inserts sample data."""
    conn = get_db()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS expenses (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                title           TEXT    NOT NULL,
                amount          REAL    NOT NULL CHECK(amount > 0),
                category        TEXT    NOT NULL,
                expense_date    TEXT    NOT NULL,
                payment_method  TEXT    NOT NULL,
                description     TEXT    DEFAULT '',
                created_at      TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
                updated_at      TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
            );

            CREATE TABLE IF NOT EXISTS budgets (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                monthly_budget  REAL    NOT NULL DEFAULT 0,
                updated_at      TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
            );
        """)
        conn.commit()
    finally:
        conn.close()


# ─── Utility Functions ─────────────────────────────────────────────────────────

def get_budget():
    """Return the latest monthly budget or 0 if none set."""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT monthly_budget FROM budgets ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return float(row["monthly_budget"]) if row else 0.0
    finally:
        conn.close()


def get_dashboard_stats():
    """Compute all dashboard totals from the database."""
    conn = get_db()
    try:
        today_str = date.today().isoformat()
        month_str = date.today().strftime("%Y-%m")

        total_all = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS s FROM expenses"
        ).fetchone()["s"]

        total_month = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS s FROM expenses "
            "WHERE strftime('%Y-%m', expense_date) = ?",
            (month_str,)
        ).fetchone()["s"]

        total_today = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS s FROM expenses "
            "WHERE expense_date = ?",
            (today_str,)
        ).fetchone()["s"]

        tx_count = conn.execute(
            "SELECT COUNT(*) AS c FROM expenses"
        ).fetchone()["c"]

        budget = get_budget()
        remaining = max(0.0, budget - total_month) if budget > 0 else 0.0
        pct = (total_month / budget * 100) if budget > 0 else 0.0
        warning = budget > 0 and (total_month / budget) >= BUDGET_WARNING_THRESHOLD

        return {
            "total_all": total_all,
            "total_month": total_month,
            "total_today": total_today,
            "tx_count": tx_count,
            "budget": budget,
            "remaining": remaining,
            "pct": round(pct, 1),
            "warning": warning,
            "month_label": date.today().strftime("%B %Y"),
        }
    finally:
        conn.close()


def validate_expense_form(form):
    """Return a list of validation error strings (empty = valid)."""
    errors = []
    title = form.get("title", "").strip()
    amount_raw = form.get("amount", "").strip()
    category = form.get("category", "").strip()
    expense_date = form.get("expense_date", "").strip()
    payment_method = form.get("payment_method", "").strip()

    if not title:
        errors.append("Expense title is required.")
    if not category or category not in CATEGORIES:
        errors.append("A valid category is required.")
    if not payment_method or payment_method not in PAYMENT_METHODS:
        errors.append("A valid payment method is required.")
    try:
        amount = float(amount_raw)
        if amount <= 0:
            errors.append("Amount must be a positive number.")
    except (ValueError, TypeError):
        errors.append("Amount must be a valid number.")
    try:
        datetime.strptime(expense_date, "%Y-%m-%d")
    except ValueError:
        errors.append("A valid date is required (YYYY-MM-DD).")
    return errors


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Home dashboard."""
    stats = get_dashboard_stats()
    conn = get_db()
    try:
        recent = conn.execute(
            "SELECT * FROM expenses ORDER BY expense_date DESC, id DESC LIMIT 5"
        ).fetchall()
    finally:
        conn.close()
    return render_template("index.html", stats=stats, recent=recent,
                           categories=CATEGORIES)


@app.route("/add")
def add():
    """Show the Add Expense form."""
    return render_template("add_expense.html",
                           categories=CATEGORIES,
                           payment_methods=PAYMENT_METHODS,
                           today=date.today().isoformat())


@app.route("/add_expense", methods=["POST"])
def add_expense():
    """Save a new expense to SQLite."""
    errors = validate_expense_form(request.form)
    if errors:
        for e in errors:
            flash(e, "danger")
        return redirect(url_for("add"))

    title = request.form["title"].strip()
    amount = float(request.form["amount"].strip())
    category = request.form["category"].strip()
    expense_date = request.form["expense_date"].strip()
    payment_method = request.form["payment_method"].strip()
    description = request.form.get("description", "").strip()

    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO expenses
               (title, amount, category, expense_date, payment_method, description)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (title, amount, category, expense_date, payment_method, description)
        )
        conn.commit()
        flash(f'Expense "{title}" of ₹{amount:.2f} added successfully!', "success")
    except Exception as ex:
        conn.rollback()
        flash(f"Error saving expense: {ex}", "danger")
    finally:
        conn.close()

    return redirect(url_for("index"))


@app.route("/expenses")
def expenses():
    """Expense history with search and filters."""
    search = request.args.get("search", "").strip()
    category_filter = request.args.get("category", "").strip()
    month_filter = request.args.get("month", "").strip()
    sort_by = request.args.get("sort", "date_desc")

    order_map = {
        "date_desc":   "expense_date DESC, id DESC",
        "date_asc":    "expense_date ASC, id ASC",
        "amount_desc": "amount DESC",
        "amount_asc":  "amount ASC",
    }
    order_clause = order_map.get(sort_by, "expense_date DESC, id DESC")

    conditions = []
    params = []

    if search:
        conditions.append("(title LIKE ? OR description LIKE ?)")
        params += [f"%{search}%", f"%{search}%"]
    if category_filter and category_filter in CATEGORIES:
        conditions.append("category = ?")
        params.append(category_filter)
    if month_filter:
        conditions.append("strftime('%Y-%m', expense_date) = ?")
        params.append(month_filter)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    query = f"SELECT * FROM expenses {where} ORDER BY {order_clause}"

    conn = get_db()
    try:
        rows = conn.execute(query, params).fetchall()
        total_filtered = conn.execute(
            f"SELECT COALESCE(SUM(amount),0) AS s FROM expenses {where}", params
        ).fetchone()["s"]
    finally:
        conn.close()

    return render_template(
        "expenses.html",
        expenses=rows,
        total_filtered=total_filtered,
        categories=CATEGORIES,
        search=search,
        category_filter=category_filter,
        month_filter=month_filter,
        sort_by=sort_by,
    )


@app.route("/edit/<int:expense_id>")
def edit(expense_id):
    """Show Edit Expense form."""
    conn = get_db()
    try:
        expense = conn.execute(
            "SELECT * FROM expenses WHERE id = ?", (expense_id,)
        ).fetchone()
    finally:
        conn.close()

    if not expense:
        flash(f"Expense #{expense_id} not found.", "danger")
        return redirect(url_for("expenses"))

    return render_template("edit_expense.html", expense=expense,
                           categories=CATEGORIES,
                           payment_methods=PAYMENT_METHODS)


@app.route("/update/<int:expense_id>", methods=["POST"])
def update(expense_id):
    """Save updated expense to SQLite."""
    conn = get_db()
    try:
        existing = conn.execute(
            "SELECT id FROM expenses WHERE id = ?", (expense_id,)
        ).fetchone()
    finally:
        conn.close()

    if not existing:
        flash(f"Expense #{expense_id} not found.", "danger")
        return redirect(url_for("expenses"))

    errors = validate_expense_form(request.form)
    if errors:
        for e in errors:
            flash(e, "danger")
        return redirect(url_for("edit", expense_id=expense_id))

    title = request.form["title"].strip()
    amount = float(request.form["amount"].strip())
    category = request.form["category"].strip()
    expense_date = request.form["expense_date"].strip()
    payment_method = request.form["payment_method"].strip()
    description = request.form.get("description", "").strip()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db()
    try:
        conn.execute(
            """UPDATE expenses
               SET title=?, amount=?, category=?, expense_date=?,
                   payment_method=?, description=?, updated_at=?
               WHERE id=?""",
            (title, amount, category, expense_date, payment_method,
             description, now, expense_id)
        )
        conn.commit()
        flash(f'Expense "{title}" updated successfully!', "success")
    except Exception as ex:
        conn.rollback()
        flash(f"Error updating expense: {ex}", "danger")
    finally:
        conn.close()

    return redirect(url_for("expenses"))


@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete(expense_id):
    """Delete an expense — POST only."""
    conn = get_db()
    try:
        existing = conn.execute(
            "SELECT title FROM expenses WHERE id = ?", (expense_id,)
        ).fetchone()
        if not existing:
            flash(f"Expense #{expense_id} not found.", "danger")
            return redirect(url_for("expenses"))
        title = existing["title"]
        conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        flash(f'Expense "{title}" deleted successfully.', "success")
    except Exception as ex:
        conn.rollback()
        flash(f"Error deleting expense: {ex}", "danger")
    finally:
        conn.close()

    return redirect(url_for("expenses"))


@app.route("/budget")
def budget():
    """Budget management page."""
    stats = get_dashboard_stats()
    return render_template("budget.html", stats=stats)


@app.route("/update_budget", methods=["POST"])
def update_budget():
    """Save or update the monthly budget."""
    raw = request.form.get("monthly_budget", "").strip()
    try:
        amount = float(raw)
        if amount < 0:
            raise ValueError("Negative budget")
    except (ValueError, TypeError):
        flash("Please enter a valid budget amount (0 or greater).", "danger")
        return redirect(url_for("budget"))

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db()
    try:
        existing = conn.execute("SELECT id FROM budgets ORDER BY id DESC LIMIT 1").fetchone()
        if existing:
            conn.execute(
                "UPDATE budgets SET monthly_budget=?, updated_at=? WHERE id=?",
                (amount, now, existing["id"])
            )
        else:
            conn.execute(
                "INSERT INTO budgets (monthly_budget, updated_at) VALUES (?, ?)",
                (amount, now)
            )
        conn.commit()
        flash(f"Monthly budget set to ₹{amount:,.2f} successfully!", "success")
    except Exception as ex:
        conn.rollback()
        flash(f"Error saving budget: {ex}", "danger")
    finally:
        conn.close()

    return redirect(url_for("budget"))


@app.route("/reports")
def reports():
    """Expense reports page."""
    conn = get_db()
    try:
        by_category = conn.execute(
            """SELECT category,
                      COUNT(*) AS cnt,
                      COALESCE(SUM(amount), 0) AS total,
                      COALESCE(AVG(amount), 0) AS avg_amt
               FROM expenses
               GROUP BY category
               ORDER BY total DESC"""
        ).fetchall()

        monthly = conn.execute(
            """SELECT strftime('%Y-%m', expense_date) AS month,
                      COUNT(*) AS cnt,
                      COALESCE(SUM(amount), 0) AS total
               FROM expenses
               GROUP BY month
               ORDER BY month DESC
               LIMIT 12"""
        ).fetchall()

        highest = conn.execute(
            "SELECT * FROM expenses ORDER BY amount DESC LIMIT 1"
        ).fetchone()

        avg_row = conn.execute(
            "SELECT COALESCE(AVG(amount), 0) AS a FROM expenses"
        ).fetchone()
        avg_expense = float(avg_row["a"])

        grand_total = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS s FROM expenses"
        ).fetchone()["s"]

        tx_count = conn.execute(
            "SELECT COUNT(*) AS c FROM expenses"
        ).fetchone()["c"]

    finally:
        conn.close()

    # Compute bar-chart widths (% relative to the highest category total)
    max_cat_total = float(by_category[0]["total"]) if by_category else 1.0
    cat_bars = []
    for row in by_category:
        pct = (float(row["total"]) / max_cat_total * 100) if max_cat_total > 0 else 0
        cat_bars.append({"row": row, "pct": round(pct, 1)})

    return render_template(
        "reports.html",
        cat_bars=cat_bars,
        monthly=monthly,
        highest=highest,
        avg_expense=avg_expense,
        grand_total=grand_total,
        tx_count=tx_count,
    )


# ─── App Entry Point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
