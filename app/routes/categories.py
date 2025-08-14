from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from app.db import db
from app.models import Category

bp = Blueprint('categories', __name__, url_prefix='/categories')

@bp.route('/')
def index():
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template('categories.html', categories=categories)

@bp.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        name = request.form['name'].strip()
        is_budgeted = request.form.get('is_budgeted') == '1'
        if not name:
            flash('Category name is required!')
        else:
            new_category = Category(name=name, is_budgeted=is_budgeted)
            db.session.add(new_category)
            db.session.commit()
            flash('Category added successfully.')
            return redirect(url_for('categories.index'))
    return render_template('category_form.html', action='Add')

@bp.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    category = Category.query.get_or_404(id)

    if request.method == 'POST':
        name = request.form['name'].strip()
        is_budgeted = request.form.get('is_budgeted') == '1'
        if not name:
            flash('Category name is required!')
        else:
            category.name = name
            category.is_budgeted = is_budgeted
            db.session.commit()
            flash('Category updated successfully.')
            return redirect(url_for('categories.index'))

    return render_template('category_form.html', category=category, action='Edit')

@bp.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted.')
    return redirect(url_for('categories.index'))
