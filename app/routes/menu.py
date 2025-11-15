from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Dish, DishCategory, Product, DishIngredient, MeasurementUnit
from app import db
from datetime import datetime

bp = Blueprint('menu', __name__)

@bp.route('/menu')
@login_required
def index():
    """Show menu categories and dishes"""
    categories = DishCategory.query.all()
    selected_category_id = request.args.get('category_id', type=int)
    
    # Get all dishes grouped by category
    dishes_by_category = {}
    for category in categories:
        query = Dish.query.filter_by(CategoryID=category.CategoryID)
        if selected_category_id and selected_category_id != category.CategoryID:
            continue
        dishes = query.filter_by(IsAvailable=True).all()
        # Фільтруємо страви, для яких вистачає інгредієнтів
        dishes = [dish for dish in dishes if can_cook_dish(dish.DishID, portions=1)]
        if dishes:  # Only add categories that have dishes
            dishes_by_category[category] = dishes
    
    selected_category = DishCategory.query.get(selected_category_id) if selected_category_id else None
    
    return render_template('menu/index.html', 
                         categories=categories,
                         dishes_by_category=dishes_by_category,
                         selected_category=selected_category)

@bp.route('/menu/dishes')
@login_required
def dishes():
    category_id = request.args.get('category_id', type=int)
    available_only = request.args.get('available_only', type=bool, default=True)
    
    query = Dish.query
    if category_id:
        query = query.filter_by(CategoryID=category_id)
    if available_only:
        query = query.filter_by(IsAvailable=True)
    
    dishes = query.all()
    return render_template('menu/dishes.html', dishes=dishes)

@bp.route('/menu/dishes/new', methods=['GET', 'POST'])
@login_required
def new_dish():
    """Create a new dish"""
    if request.method == 'POST':
        name = request.form.get('name')
        category_id = request.form.get('category_id')
        price = request.form.get('price')
        description = request.form.get('description')
        is_available = bool(request.form.get('is_available'))
        
        if not all([name, category_id, price]):
            flash('Всі поля повинні бути заповнені', 'danger')
            return redirect(url_for('menu.new_dish'))
        
        try:
            price = float(price)
            if price <= 0:
                raise ValueError
        except ValueError:
            flash('Некоректна ціна', 'danger')
            return redirect(url_for('menu.new_dish'))
        
        dish = Dish(
            DishName=name,
            CategoryID=category_id,
            Price=price,
            Description=description,
            IsAvailable=is_available,
            ValidFrom=datetime.now()
        )
        db.session.add(dish)
        db.session.commit()
        
        flash('Страву додано', 'success')
        return redirect(url_for('menu.edit_recipe', dish_id=dish.DishID))
    
    categories = DishCategory.query.all()
    return render_template('menu/new_dish.html', categories=categories)

@bp.route('/menu/dishes/<int:dish_id>')
@login_required
def view_dish(dish_id):
    dish = Dish.query.get_or_404(dish_id)
    return render_template('menu/view_dish.html', dish=dish)

@bp.route('/menu/dishes/<int:dish_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_dish(dish_id):
    """Edit an existing dish"""
    dish = Dish.query.get_or_404(dish_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        category_id = request.form.get('category_id')
        price = request.form.get('price')
        description = request.form.get('description')
        is_available = bool(request.form.get('is_available'))
        
        if not all([name, category_id, price]):
            flash('Всі поля повинні бути заповнені', 'danger')
            return redirect(url_for('menu.edit_dish', dish_id=dish_id))
        
        try:
            price = float(price)
            if price <= 0:
                raise ValueError
        except ValueError:
            flash('Некоректна ціна', 'danger')
            return redirect(url_for('menu.edit_dish', dish_id=dish_id))
        
        # If price changed, archive current price and create new one
        if price != dish.Price:
            dish.ValidTo = datetime.now()
            new_dish = Dish(
                DishName=name,
                CategoryID=category_id,
                Price=price,
                Description=description,
                IsAvailable=is_available,
                ValidFrom=datetime.now()
            )
            db.session.add(new_dish)
        else:
            dish.DishName = name
            dish.CategoryID = category_id
            dish.Description = description
            dish.IsAvailable = is_available
        
        db.session.commit()
        flash('Страву оновлено', 'success')
        return redirect(url_for('menu.index'))
    
    categories = DishCategory.query.all()
    return render_template('menu/edit_dish.html', dish=dish, categories=categories)

@bp.route('/menu/dishes/<int:dish_id>/recipe', methods=['GET', 'POST'])
@login_required
def edit_recipe(dish_id):
    """Edit dish recipe (ingredients)"""
    dish = Dish.query.get_or_404(dish_id)
    
    if request.method == 'POST':
        # Clear existing ingredients
        DishIngredient.query.filter_by(DishID=dish_id).delete()
        
        # Add new ingredients
        ingredients = request.json.get('ingredients', [])
        for ingredient in ingredients:
            dish_ingredient = DishIngredient(
                DishID=dish_id,
                ProductID=ingredient['product_id'],
                Quantity=ingredient['quantity']
            )
            db.session.add(dish_ingredient)
        
        db.session.commit()
        return jsonify({'status': 'success'})
    
    products = Product.query.filter_by(IsAvailable=True).all()
    return render_template('menu/edit_recipe.html', dish=dish, products=products)

@bp.route('/menu/dishes/<int:dish_id>/toggle', methods=['POST'])
@login_required
def toggle_availability(dish_id):
    """Toggle dish availability"""
    dish = Dish.query.get_or_404(dish_id)
    dish.IsAvailable = not dish.IsAvailable
    db.session.commit()
    
    status = 'доступна' if dish.IsAvailable else 'недоступна'
    flash(f'Страва тепер {status}', 'success')
    return redirect(url_for('menu.index'))

@bp.route('/menu/dishes/<int:dish_id>/delete', methods=['POST'])
@login_required
def delete_dish(dish_id):
    """Delete a dish"""
    if current_user.role.RoleName != 'Адміністратор':
        flash('Тільки адміністратор може видаляти страви', 'danger')
        return redirect(url_for('menu.index'))
    
    dish = Dish.query.get_or_404(dish_id)
    
    try:
        # Delete ingredients first
        DishIngredient.query.filter_by(DishID=dish_id).delete()
        db.session.delete(dish)
        db.session.commit()
        flash('Страву видалено', 'success')
    except:
        db.session.rollback()
        flash('Неможливо видалити страву, яка є в замовленнях', 'danger')
    
    return redirect(url_for('menu.index'))

@bp.route('/menu/categories')
@login_required
def categories():
    categories = DishCategory.query.all()
    return render_template('menu/categories.html', categories=categories)

@bp.route('/menu/categories/new', methods=['GET', 'POST'])
@login_required
def new_category():
    """Create a new dish category"""
    if current_user.role.RoleName != 'Адміністратор':
        flash('Тільки адміністратор може створювати категорії', 'danger')
        return redirect(url_for('menu.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        unit_id = request.form.get('unit_id')
        
        if not name or not unit_id:
            flash('Всі поля повинні бути заповнені', 'danger')
            return redirect(url_for('menu.new_category'))
        
        category = DishCategory(
            CategoryName=name,
            MeasurementUnitID=unit_id
        )
        db.session.add(category)
        db.session.commit()
        
        flash('Категорію додано', 'success')
        return redirect(url_for('menu.index'))
    
    units = MeasurementUnit.query.all()
    return render_template('menu/new_category.html', units=units)

@bp.route('/menu/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    """Edit a dish category"""
    if current_user.role.RoleName != 'Адміністратор':
        flash('Тільки адміністратор може редагувати категорії', 'danger')
        return redirect(url_for('menu.index'))
    
    category = DishCategory.query.get_or_404(category_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        unit_id = request.form.get('unit_id')
        
        if not name or not unit_id:
            flash('Всі поля повинні бути заповнені', 'danger')
            return redirect(url_for('menu.edit_category', category_id=category_id))
        
        category.CategoryName = name
        category.MeasurementUnitID = unit_id
        db.session.commit()
        
        flash('Категорію оновлено', 'success')
        return redirect(url_for('menu.index'))
    
    units = MeasurementUnit.query.all()
    return render_template('menu/edit_category.html', category=category, units=units)

@bp.route('/menu/ingredients')
@login_required
def ingredients():
    products = Product.query.all()
    return render_template('menu/ingredients.html', products=products)

@bp.route('/menu/ingredients/new', methods=['GET', 'POST'])
@login_required
def new_ingredient():
    if request.method == 'POST':
        name = request.form.get('name')
        unit_id = request.form.get('unit_id')
        description = request.form.get('description')
        
        product = Product(
            ProductName=name,
            MeasurementUnitID=unit_id,
            Description=description,
            IsAvailable=True
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Інгредієнт додано', 'success')
        return redirect(url_for('menu.ingredients'))
    
    units = MeasurementUnit.query.all()
    return render_template('menu/new_ingredient.html', units=units)

@bp.route('/menu/dishes/<int:dish_id>/ingredients', methods=['GET', 'POST'])
@login_required
def dish_ingredients(dish_id):
    dish = Dish.query.get_or_404(dish_id)
    
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')
        
        ingredient = DishIngredient(
            DishID=dish_id,
            ProductID=product_id,
            Quantity=quantity
        )
        
        db.session.add(ingredient)
        db.session.commit()
        
        flash('Інгредієнт додано до страви', 'success')
        return redirect(url_for('menu.dish_ingredients', dish_id=dish_id))
    
    products = Product.query.filter_by(IsAvailable=True).all()
    return render_template('menu/dish_ingredients.html', dish=dish, products=products)

def can_cook_dish(dish_id, portions=1):
    ingredients = DishIngredient.query.filter_by(DishID=dish_id).all()
    for ingredient in ingredients:
        product = Product.query.get(ingredient.ProductID)
        if not product or not product.IsAvailable:
            return False
        if product.Quantity < ingredient.Quantity * portions:
            return False
    return True

@bp.app_context_processor
def inject_can_cook_dish():
    return dict(can_cook_dish=can_cook_dish) 