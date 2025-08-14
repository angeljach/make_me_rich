from flask import (
    Blueprint, render_template, request, redirect, url_for
)
from collections import defaultdict
from datetime import datetime
from app.db import get_db

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return redirect(url_for('main.dashboard'))

@bp.route('/dashboard')
def dashboard():
    year = request.args.get('year', default=None, type=int)
    month = request.args.get('month', default=None, type=int)
    is_budgeted_filter = request.args.get('is_budgeted_filter', default='all')

    now = datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month

    db = get_db()
    base_query = '''
        SELECT e.*, c.name as category_name, c.is_budgeted
        FROM expenses e
        LEFT JOIN categories c ON e.category_id = c.id
        WHERE strftime("%Y", event_date) = ? AND strftime("%m", event_date) = ?
    '''
    params = [str(year), f"{month:02d}"]

    if is_budgeted_filter == 'budgeted':
        base_query += ' AND c.is_budgeted = 1'
    elif is_budgeted_filter == 'not_budgeted':
        base_query += ' AND (c.is_budgeted = 0 OR c.is_budgeted IS NULL)'

    base_query += ' ORDER BY event_date ASC'
    expenses = db.execute(base_query, tuple(params)).fetchall()

    daily_expenses = defaultdict(float)
    for exp in expenses:
        daily_expenses[exp['event_date']] += exp['amount']

    monthly_expense_total = sum(exp['amount'] for exp in expenses)

    category_expenses = defaultdict(float)
    for exp in expenses:
        category = exp['category_name'] or 'Uncategorized'
        category_expenses[category] += exp['amount']

    top_day = max(daily_expenses.items(), key=lambda x: x[1]) if daily_expenses else (None, 0)
    high_expense = max(expenses, key=lambda x: x['amount']) if expenses else None

    return render_template('dashboard.html',
                           year=year,
                           month=month,
                           daily_expenses=daily_expenses,
                           monthly_expense_total=monthly_expense_total,
                           category_expenses=category_expenses,
                           top_day=top_day,
                           high_expense=high_expense,
                           is_budgeted_filter=is_budgeted_filter)
