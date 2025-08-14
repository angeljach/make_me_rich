from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from app.db import get_db

bp = Blueprint('expenses', __name__, url_prefix='/expenses')

@bp.route('/')
def index():
    db = get_db()
    expenses = db.execute('''
        SELECT e.*, c.name as category_name, p.name as payment_type_name
        FROM expenses e
        LEFT JOIN categories c ON e.category_id = c.id
        LEFT JOIN payment_types p ON e.payment_type_id = p.id
        ORDER BY e.event_date DESC
    ''').fetchall()
    categories = db.execute('SELECT * FROM categories ORDER BY name ASC').fetchall()
    payment_types = db.execute('SELECT * FROM payment_types ORDER BY name ASC').fetchall()
    return render_template('expenses.html', expenses=expenses, categories=categories, payment_types=payment_types)

@bp.route('/add', methods=('GET', 'POST'))
def add():
    db = get_db()
    categories = db.execute('SELECT * FROM categories ORDER BY name ASC').fetchall()
    payment_types = db.execute('SELECT * FROM payment_types ORDER BY name ASC').fetchall()

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
                float(amount)
            except ValueError:
                error = 'Amount must be a number.'

        if error:
            flash(error)
        else:
            db.execute('''
                INSERT INTO expenses (event_date, amount, name, category_id, payment_type_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (event_date, amount, name or None, category_id or None, payment_type_id or None))
            db.commit()
            flash('Expense added successfully.')
            return redirect(url_for('expenses.index'))

    return render_template('expense_form.html', categories=categories, payment_types=payment_types, action='Add')

@bp.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    db = get_db()
    expense = db.execute('SELECT * FROM expenses WHERE id = ?', (id,)).fetchone()
    if expense is None:
        flash('Expense not found.')
        return redirect(url_for('expenses.index'))

    categories = db.execute('SELECT * FROM categories ORDER BY name ASC').fetchall()
    payment_types = db.execute('SELECT * FROM payment_types ORDER BY name ASC').fetchall()

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
                float(amount)
            except ValueError:
                error = 'Amount must be a number.'

        if error:
            flash(error)
        else:
            db.execute('''
                UPDATE expenses
                SET event_date = ?, amount = ?, name = ?, category_id = ?, payment_type_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (event_date, amount, name or None, category_id or None, payment_type_id or None, id))
            db.commit()
            flash('Expense updated successfully.')
            return redirect(url_for('expenses.index'))

    return render_template('expense_form.html', expense=expense, categories=categories, payment_types=payment_types, action='Edit')

@bp.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    db = get_db()
    db.execute('DELETE FROM expenses WHERE id = ?', (id,))
    db.commit()
    flash('Expense deleted.')
    return redirect(url_for('expenses.index'))

@bp.route('/copy/<int:id>', methods=('POST',))
def copy(id):
    db = get_db()
    expense = db.execute('SELECT * FROM expenses WHERE id = ?', (id,)).fetchone()
    if expense is None:
        flash('Expense not found.', 'danger')
        return redirect(url_for('expenses.index'))

    db.execute('''
        INSERT INTO expenses (event_date, amount, name, category_id, payment_type_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (expense['event_date'], expense['amount'], expense['name'], expense['category_id'], expense['payment_type_id']))
    db.commit()
    flash('Expense copied successfully.', 'success')
    return redirect(url_for('expenses.index'))
