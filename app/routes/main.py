from flask import (
    Blueprint, render_template, request, redirect, url_for
)
from collections import defaultdict
from datetime import datetime
from app.db import db
from app.models import Expense, Category
from sqlalchemy import extract

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

    query = Expense.query.join(Category, Expense.category_id == Category.id, isouter=True).filter(
        extract('year', Expense.event_date) == year,
        extract('month', Expense.event_date) == month
    )

    if is_budgeted_filter == 'budgeted':
        query = query.filter(Category.is_budgeted == True)
    elif is_budgeted_filter == 'not_budgeted':
        query = query.filter((Category.is_budgeted == False) | (Category.is_budgeted == None))

    expenses = query.order_by(Expense.event_date.asc()).all()

    daily_expenses = defaultdict(float)
    for exp in expenses:
        daily_expenses[exp.event_date.strftime('%Y-%m-%d')] += exp.amount

    monthly_expense_total = sum(exp.amount for exp in expenses)

    category_expenses = defaultdict(float)
    for exp in expenses:
        category = exp.category.name if exp.category else 'Uncategorized'
        category_expenses[category] += exp.amount

    top_day = max(daily_expenses.items(), key=lambda x: x[1]) if daily_expenses else (None, 0)
    high_expense = max(expenses, key=lambda x: x.amount) if expenses else None

    return render_template('dashboard.html',
                           year=year,
                           month=month,
                           daily_expenses=daily_expenses,
                           monthly_expense_total=monthly_expense_total,
                           category_expenses=category_expenses,
                           top_day=top_day,
                           high_expense=high_expense,
                           is_budgeted_filter=is_budgeted_filter)
