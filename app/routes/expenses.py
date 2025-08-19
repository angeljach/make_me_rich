from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from app.db import db
from app.models import Expense, Category, PaymentType
from sqlalchemy.orm import joinedload
from datetime import datetime

bp = Blueprint('expenses', __name__, url_prefix='/expenses')

@bp.route('/')
def index():
    expenses = Expense.query.options(joinedload(Expense.category), joinedload(Expense.payment_type)).order_by(Expense.event_date.desc()).all()
    categories = Category.query.order_by(Category.name.asc()).all()
    payment_types = PaymentType.query.order_by(PaymentType.name.asc()).all()
    return render_template('expenses.html', expenses=expenses, categories=categories, payment_types=payment_types)

@bp.route('/add', methods=('GET', 'POST'))
def add():
    categories = Category.query.order_by(Category.name.asc()).all()
    payment_types = PaymentType.query.order_by(PaymentType.name.asc()).all()

    if request.method == 'POST':
        name = request.form['name'].strip()
        event_date = datetime.strptime(request.form['event_date'], '%Y-%m-%d').date()
        amount = float(request.form['amount'])
        category_id = request.form.get('category_id')
        payment_type_id = request.form.get('payment_type_id')

        new_expense = Expense(
            name=name,
            event_date=event_date,
            amount=amount,
            category_id=category_id if category_id else None,
            payment_type_id=payment_type_id if payment_type_id else None
        )
        db.session.add(new_expense)
        db.session.commit()
        flash('Expense added successfully.')
        return redirect(url_for('expenses.index'))

    return render_template('expense_form.html', categories=categories, payment_types=payment_types, action='Add')

@bp.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    expense = Expense.query.get_or_404(id)
    categories = Category.query.order_by(Category.name.asc()).all()
    payment_types = PaymentType.query.order_by(PaymentType.name.asc()).all()

    if request.method == 'POST':
        expense.name = request.form['name'].strip()
        expense.event_date = datetime.strptime(request.form['event_date'], '%Y-%m-%d').date()
        expense.amount = float(request.form['amount'])
        expense.category_id = request.form.get('category_id') if request.form.get('category_id') else None
        expense.payment_type_id = request.form.get('payment_type_id') if request.form.get('payment_type_id') else None

        db.session.commit()
        flash('Expense updated successfully.')
        return redirect(url_for('expenses.index'))

    return render_template('expense_form.html', expense=expense, categories=categories, payment_types=payment_types, action='Edit')

@bp.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted.')
    return redirect(url_for('expenses.index'))

@bp.route('/copy/<int:id>', methods=('POST',))
def copy(id):
    expense_to_copy = Expense.query.get_or_404(id)
    new_expense = Expense(
        name=expense_to_copy.name,
        event_date=expense_to_copy.event_date,
        amount=expense_to_copy.amount,
        category_id=expense_to_copy.category_id,
        payment_type_id=expense_to_copy.payment_type_id
    )
    db.session.add(new_expense)
    db.session.commit()
    flash('Expense copied successfully.', 'success')
    return redirect(url_for('expenses.index'))
