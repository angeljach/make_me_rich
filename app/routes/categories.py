from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from app.db import get_db

bp = Blueprint('categories', __name__, url_prefix='/categories')

@bp.route('/')
def index():
    db = get_db()
    categories = db.execute('SELECT * FROM categories ORDER BY name ASC').fetchall()
    return render_template('categories.html', categories=categories)

@bp.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        name = request.form['name'].strip()
        is_budgeted = request.form.get('is_budgeted') == '1'
        if not name:
            flash('Category name is required!')
        else:
            db = get_db()
            db.execute('INSERT INTO categories (name, is_budgeted) VALUES (?, ?)', (name, is_budgeted))
            db.commit()
            flash('Category added successfully.')
            return redirect(url_for('categories.index'))
    return render_template('category_form.html', action='Add')

@bp.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    db = get_db()
    category = db.execute('SELECT * FROM categories WHERE id = ?', (id,)).fetchone()
    if category is None:
        flash('Category not found.')
        return redirect(url_for('categories.index'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        is_budgeted = request.form.get('is_budgeted') == '1'
        if not name:
            flash('Category name is required!')
        else:
            db.execute('UPDATE categories SET name = ?, is_budgeted = ? WHERE id = ?', (name, is_budgeted, id))
            db.commit()
            flash('Category updated successfully.')
            return redirect(url_for('categories.index'))

    return render_template('category_form.html', category=category, action='Edit')

@bp.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    db = get_db()
    db.execute('DELETE FROM categories WHERE id = ?', (id,))
    db.commit()
    flash('Category deleted.')
    return redirect(url_for('categories.index'))
