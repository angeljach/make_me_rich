from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime, date
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this for production!

DATABASE = 'data/expenses.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Home redirect
@app.route('/')
def home():
    return redirect(url_for('dashboard'))

# Categories CRUD
@app.route('/categories')
def categories():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    conn.close()
    return render_template('categories.html', categories=categories)

@app.route('/categories/add', methods=('GET', 'POST'))
def add_category():
    if request.method == 'POST':
        name = request.form['name'].strip()
        if not name:
            flash('Category name is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO categories (name) VALUES (?)', (name,))
            conn.commit()
            conn.close()
            flash('Category added successfully.')
            return redirect(url_for('categories'))
    return render_template('category_form.html', action='Add')

@app.route('/categories/edit/<int:id>', methods=('GET', 'POST'))
def edit_category(id):
    conn = get_db_connection()
    category = conn.execute('SELECT * FROM categories WHERE id = ?', (id,)).fetchone()

    if category is None:
        flash('Category not found.')
        return redirect(url_for('categories'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        if not name:
            flash('Category name is required!')
        else:
            conn.execute('UPDATE categories SET name = ? WHERE id = ?', (name, id))
            conn.commit()
            conn.close()
            flash('Category updated successfully.')
            return redirect(url_for('categories'))

    conn.close()
    return render_template('category_form.html', category=category, action='Edit')

@app.route('/categories/delete/<int:id>', methods=('POST',))
def delete_category(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM categories WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Category deleted.')
    return redirect(url_for('categories'))

# Expenses CRUD
@app.route('/expenses')
def expenses():
    conn = get_db_connection()
    expenses = conn.execute('''
        SELECT e.*, c.name as category_name, p.name as payment_type_name
        FROM expenses e
        LEFT JOIN categories c ON e.category_id = c.id
        LEFT JOIN payment_types p ON e.payment_type_id = p.id
        ORDER BY e.event_date DESC
    ''').fetchall()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    payment_types = conn.execute('SELECT * FROM payment_types').fetchall()
    conn.close()
    return render_template('expenses.html', expenses=expenses, categories=categories, payment_types=payment_types)

@app.route('/expenses/add', methods=('GET', 'POST'))
def add_expense():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories ORDER BY name ASC').fetchall()
    payment_types = conn.execute('SELECT * FROM payment_types ORDER BY name ASC').fetchall()

    if request.method == 'POST':
        name = request.form['name'].strip()
        event_date = request.form['event_date']
        amount = request.form['amount']
        category_id = request.form.get('category_id')
        payment_type_id = request.form.get('payment_type_id')

        error = None
        if not event_date:
            error = 'Date is required.'
        elif not amount:
            error = 'Amount is required.'
        else:
            try:
                amount = float(amount)
            except ValueError:
                error = 'Amount must be a number.'

        if error:
            flash(error)
        else:
            conn.execute('''
                INSERT INTO expenses (event_date, amount, name, category_id, payment_type_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (event_date, amount, name if name else None, category_id if category_id else None, payment_type_id if payment_type_id else None))
            conn.commit()
            conn.close()
            flash('Expense added successfully.')
            return redirect(url_for('expenses'))

    conn.close()
    return render_template('expense_form.html', categories=categories, payment_types=payment_types, action='Add')

@app.route('/expenses/edit/<int:id>', methods=('GET', 'POST'))
def edit_expense(id):
    conn = get_db_connection()
    expense = conn.execute('SELECT * FROM expenses WHERE id = ?', (id,)).fetchone()
    if expense is None:
        flash('Expense not found.')
        return redirect(url_for('expenses'))

    categories = conn.execute('SELECT * FROM categories').fetchall()
    payment_types = conn.execute('SELECT * FROM payment_types').fetchall()

    if request.method == 'POST':
        name = request.form['name'].strip()
        event_date = request.form['event_date']
        amount = request.form['amount']
        category_id = request.form.get('category_id')
        payment_type_id = request.form.get('payment_type_id')

        error = None
        if not event_date:
            error = 'Date is required.'
        elif not amount:
            error = 'Amount is required.'
        else:
            try:
                amount = float(amount)
            except ValueError:
                error = 'Amount must be a number.'

        if error:
            flash(error)
        else:
            conn.execute('''
                UPDATE expenses
                SET event_date = ?, amount = ?, name = ?, category_id = ?, payment_type_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (event_date, amount, name if name else None, category_id if category_id else None, payment_type_id if payment_type_id else None, id))
            conn.commit()
            conn.close()
            flash('Expense updated successfully.')
            return redirect(url_for('expenses'))

    conn.close()
    return render_template('expense_form.html', expense=expense, categories=categories, payment_types=payment_types, action='Edit')


@app.route('/expenses/delete/<int:id>', methods=('POST',))
def delete_expense(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM expenses WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Expense deleted.')
    return redirect(url_for('expenses'))

# Dashboard with graphs
@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()

    # Filter only current month expenses
    today = date.today()
    first_day = today.replace(day=1).isoformat()

    expenses = conn.execute('''
        SELECT e.*, c.name as category_name
        FROM expenses e
        LEFT JOIN categories c ON e.category_id = c.id
        WHERE event_date >= ?
        ORDER BY event_date ASC
    ''', (first_day,)).fetchall()

    # Prepare data for graphs:

    # 1) Daily expenses for current month
    daily_expenses = defaultdict(float)
    for exp in expenses:
        daily_expenses[exp['event_date']] += exp['amount']

    # 2) Monthly expenses (sum for current month)
    monthly_expense_total = sum(exp['amount'] for exp in expenses)

    # 3) Expenses by category
    category_expenses = defaultdict(float)
    for exp in expenses:
        category = exp['category_name'] or 'Uncategorized'
        category_expenses[category] += exp['amount']

    # 4) Top day expense of the month
    if daily_expenses:
        top_day = max(daily_expenses.items(), key=lambda x: x[1])
    else:
        top_day = (None, 0)

    # 5) High expense of the month
    if expenses:
        high_expense = max(expenses, key=lambda x: x['amount'])
    else:
        high_expense = None

    conn.close()
    return render_template('dashboard.html',
                           daily_expenses=daily_expenses,
                           monthly_expense_total=monthly_expense_total,
                           category_expenses=category_expenses,
                           top_day=top_day,
                           high_expense=high_expense,
                           today=today.isoformat()
                           )

if __name__ == '__main__':
    app.run(debug=True, port=5001)
