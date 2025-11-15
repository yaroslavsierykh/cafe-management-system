from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app.models import Product, MeasurementUnit
from app import db

bp = Blueprint('products', __name__)

@bp.route('/products')
@login_required
def index():
    """Show list of products"""
    products = Product.query.all()
    return render_template('products/index.html', products=products)

@bp.route('/products/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create a new product"""
    if request.method == 'POST':
        name = request.form.get('name')
        unit_id = request.form.get('unit_id')
        description = request.form.get('description')
        is_available = bool(request.form.get('is_available'))
        quantity = request.form.get('quantity', type=float) or 0
        
        if not name or not unit_id:
            flash('Назва та одиниця виміру обов\'язкові', 'danger')
            return redirect(url_for('products.new'))
        
        product = Product(
            ProductName=name,
            MeasurementUnitID=unit_id,
            Description=description,
            IsAvailable=is_available,
            Quantity=quantity
        )
        db.session.add(product)
        db.session.commit()
        
        flash('Продукт додано', 'success')
        return redirect(url_for('products.index'))
    
    units = MeasurementUnit.query.all()
    current_app.logger.debug(f'Rendering new product form with {len(units)} measurement units')
    current_app.logger.debug(f'Units: {[unit.UnitName for unit in units]}')
    return render_template('products/new.html', units=units)

@bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(product_id):
    """Edit an existing product"""
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        unit_id = request.form.get('unit_id')
        description = request.form.get('description')
        is_available = bool(request.form.get('is_available'))
        quantity = request.form.get('quantity', type=float) or 0
        
        if not name or not unit_id:
            flash('Назва та одиниця виміру обов\'язкові', 'danger')
            return redirect(url_for('products.edit', product_id=product_id))
        
        product.ProductName = name
        product.MeasurementUnitID = unit_id
        product.Description = description
        product.IsAvailable = is_available
        product.Quantity = quantity
        
        db.session.commit()
        flash('Продукт оновлено', 'success')
        return redirect(url_for('products.index'))
    
    units = MeasurementUnit.query.all()
    return render_template('products/edit.html', product=product, units=units)

@bp.route('/products/<int:product_id>/toggle', methods=['POST'])
@login_required
def toggle_availability(product_id):
    """Toggle product availability"""
    product = Product.query.get_or_404(product_id)
    product.IsAvailable = not product.IsAvailable
    db.session.commit()
    
    status = 'доступний' if product.IsAvailable else 'недоступний'
    flash(f'Продукт тепер {status}', 'success')
    return redirect(url_for('products.index'))

@bp.route('/products/<int:product_id>/delete', methods=['POST'])
@login_required
def delete(product_id):
    """Delete a product"""
    if current_user.role.RoleName != 'Адміністратор':
        flash('Тільки адміністратор може видаляти продукти', 'danger')
        return redirect(url_for('products.index'))
    
    product = Product.query.get_or_404(product_id)
    
    try:
        db.session.delete(product)
        db.session.commit()
        flash('Продукт видалено', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Неможливо видалити продукт, який використовується в рецептах', 'danger')
    
    return redirect(url_for('products.index'))

@bp.route('/products/<int:product_id>/change_quantity', methods=['POST'])
@login_required
def change_quantity(product_id):
    """Change product quantity"""
    product = Product.query.get_or_404(product_id)
    try:
        new_quantity = float(request.form.get('new_quantity', 0))
        if new_quantity < 0:
            return {'success': False, 'error': 'Кількість не може бути від\'ємною'}
        product.Quantity = new_quantity
        db.session.commit()
        return {'success': True}
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'error': str(e)} 