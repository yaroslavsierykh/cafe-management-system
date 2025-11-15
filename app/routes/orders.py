from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app.models import Order, OrderStatus, OrderType, Customer, Person, Dish, OrderDish, PaymentMethod, Hall, CafeTable, StreetType, TableStatus, SeatStatus, DishCategory, DishIngredient, Product, Payment, Shift
from app import db
from datetime import datetime
from app.routes.menu import can_cook_dish

bp = Blueprint('orders', __name__, url_prefix='/orders')

@bp.route('/orders')
@login_required
def index():
    """Show list of orders for current shift"""
    status = request.args.get('status', 'active')
    current_shift = current_user.current_shift
    if not current_shift:
        flash('Відкрийте зміну, щоб переглядати замовлення', 'warning')
        return render_template('orders/index.html', orders=[])
    query = Order.query.filter_by(ShiftID=current_shift.ShiftID)
    if status == 'active':
        query = query.join(OrderStatus).filter(
            OrderStatus.StatusName.in_(['Нове', 'Готується'])
        )
    orders = query.order_by(Order.OrderDateTime.desc()).all()
    return render_template('orders/index.html', orders=orders)

@bp.route('/orders/new')
@login_required
def new():
    """Create new order"""
    halls = Hall.query.all()
    customers = Customer.query.all()
    street_types = StreetType.query.all()
    return render_template('orders/new.html', 
                         halls=halls,
                         customers=customers,
                         street_types=street_types)

@bp.route('/orders/new', methods=['GET', 'POST'])
@login_required
def new_order():
    current_shift = current_user.current_shift
    if not current_shift:
        flash('Неможливо створити замовлення: зміна не відкрита', 'danger')
        return redirect(url_for('orders.index'))
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        table_id = request.form.get('table_id')
        order_type_id = request.form.get('order_type_id')
        address_id = request.form.get('address_id')
        
        # Validate delivery order requirements
        if order_type_id == '2':  # Delivery order
            if not customer_id:
                flash('Для замовлення доставки необхідно вибрати клієнта', 'danger')
                return redirect(url_for('orders.new'))
            if not address_id:
                flash('Для замовлення доставки необхідно вказати адресу доставки', 'danger')
                return redirect(url_for('orders.new'))
        
        # Create new order
        order = Order(
            CustomerID=customer_id if customer_id else None,
            EmployeeID=current_user.EmployeeID,
            TableID=table_id if table_id else None,
            OrderTypeID=order_type_id,
            OrderStatusID=OrderStatus.query.filter_by(StatusName='Нове').first().OrderStatusID,
            OrderDateTime=datetime.utcnow(),
            TotalAmount=0,  # Initialize TotalAmount to 0
            ShiftID=current_shift.ShiftID,
            AddressID=address_id if address_id and order_type_id == '2' else None  # Set address only for delivery orders
        )
        db.session.add(order)
        # Update table status if it's a table order
        if table_id:
            table = CafeTable.query.get(table_id)
            occupied_status = TableStatus.query.filter_by(StatusName='Зайнятий').first()
            table.TableStatusID = occupied_status.TableStatusID
            # Update seat statuses
            for seat in table.seats:
                occupied_seat_status = SeatStatus.query.filter_by(StatusName='Зайняте').first()
                seat.SeatStatusID = occupied_seat_status.SeatStatusID
        db.session.commit()
        flash('Замовлення створено', 'success')
        return redirect(url_for('orders.view_order', order_id=order.OrderID))
    halls = Hall.query.all()
    customers = Customer.query.all()
    street_types = StreetType.query.all()
    return render_template('orders/new.html', 
                         halls=halls,
                         customers=customers,
                         street_types=street_types)

@bp.route('/<int:order_id>')
@login_required
def view_order(order_id):
    order = Order.query.get_or_404(order_id)
    categories = DishCategory.query.all()
    payment_methods = PaymentMethod.query.all()
    halls = Hall.query.all()
    return render_template('orders/view.html', order=order, categories=categories, payment_methods=payment_methods, halls=halls)

@bp.route('/<int:order_id>/change_table', methods=['POST'])
@login_required
def change_table(order_id):
    order = Order.query.get_or_404(order_id)
    new_table_id = request.form.get('table_id')
    
    if not new_table_id:
        return jsonify({'error': 'Необхідно вибрати стіл'})
    
    # Check if new table is available
    new_table = CafeTable.query.get(new_table_id)
    if not new_table:
        return jsonify({'error': 'Стіл не знайдено'})
    
    # Free up the old table if it exists
    if order.TableID:
        old_table = CafeTable.query.get(order.TableID)
        if old_table:
            free_status = TableStatus.query.filter_by(StatusName='Вільний').first()
            old_table.TableStatusID = free_status.TableStatusID
            # Update seat statuses
            for seat in old_table.seats:
                free_seat_status = SeatStatus.query.filter_by(StatusName='Вільне').first()
                seat.SeatStatusID = free_seat_status.SeatStatusID
    
    # Update order with new table
    order.TableID = new_table_id
    
    # Mark new table as occupied
    occupied_status = TableStatus.query.filter_by(StatusName='Зайнятий').first()
    new_table.TableStatusID = occupied_status.TableStatusID
    # Update seat statuses
    for seat in new_table.seats:
        occupied_seat_status = SeatStatus.query.filter_by(StatusName='Зайняте').first()
        seat.SeatStatusID = occupied_seat_status.SeatStatusID
    
    db.session.commit()
    return jsonify({'message': 'Стіл успішно змінено'})

@bp.route('/orders/<int:order_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(order_id):
    order = Order.query.get_or_404(order_id)
    
    if request.method == 'POST':
        # Update order details
        customer_id = request.form.get('customer_id')
        table_id = request.form.get('table_id')
        status_id = request.form.get('status_id')
        
        order.CustomerID = customer_id if customer_id else None
        order.TableID = table_id if table_id else None
        order.OrderStatusID = status_id
        
        db.session.commit()
        flash('Замовлення оновлено', 'success')
        return redirect(url_for('orders.view_order', order_id=order.OrderID))
    
    halls = Hall.query.all()
    customers = Customer.query.all()
    order_statuses = OrderStatus.query.all()
    return render_template('orders/edit.html', 
                         order=order,
                         halls=halls,
                         customers=customers,
                         order_statuses=order_statuses)

@bp.route('/orders/<int:order_id>/add_dish', methods=['POST'])
@login_required
def add_dish(order_id):
    order = Order.query.get_or_404(order_id)
    dish_id = request.form.get('dish_id')
    quantity = request.form.get('quantity', type=int)
    note = request.form.get('note')
    
    if not dish_id or not quantity:
        return jsonify({'error': 'Необхідно вказати страву та кількість'})
    
    dish = Dish.query.get_or_404(dish_id)
    
    # Check if dish can be cooked (all ingredients are available and enough quantity)
    if not can_cook_dish(dish_id, portions=quantity):
        return jsonify({'error': 'Страва недоступна - недостатньо інгредієнтів на складі'})
    
    # Check if dish is already in order
    existing_dish = OrderDish.query.filter_by(
        OrderID=order_id,
        DishID=dish_id
    ).first()
    
    if existing_dish:
        existing_dish.Quantity += quantity
        # Якщо нотатка передана, оновити її
        if note is not None:
            existing_dish.Notes = note
        # Update total amount
        order.TotalAmount += dish.Price * quantity
    else:
        order_dish = OrderDish(
            OrderID=order_id,
            DishID=dish_id,
            Quantity=quantity,
            PriceAtTime=dish.Price,
            Notes=note
        )
        db.session.add(order_dish)
        # Update total amount
        order.TotalAmount += dish.Price * quantity
    
    # Deduct ingredients from stock
    ingredients = DishIngredient.query.filter_by(DishID=dish_id).all()
    for ingredient in ingredients:
        product = Product.query.get(ingredient.ProductID)
        if product:
            product.Quantity -= ingredient.Quantity * quantity
            if product.Quantity < 0:
                product.Quantity = 0
    
    db.session.commit()
    return jsonify({'message': 'Страву додано до замовлення'})

@bp.route('/orders/<int:order_id>/remove_dish/<int:order_dish_id>', methods=['POST'])
@login_required
def remove_dish(order_id, order_dish_id):
    order = Order.query.get_or_404(order_id)
    order_dish = OrderDish.query.get_or_404(order_dish_id)
    
    if order_dish.OrderID != order_id:
        abort(404)
    
    quantity_to_remove = request.form.get('quantity', type=int)
    if not quantity_to_remove or quantity_to_remove < 1:
        return jsonify({'error': 'Необхідно вказати кількість для видалення (мінімум 1)'})
    
    if quantity_to_remove > order_dish.Quantity:
        return jsonify({'error': 'Кількість для видалення не може перевищувати загальну кількість'})
    
    # Update total amount
    order.TotalAmount -= order_dish.PriceAtTime * quantity_to_remove

    # Повертаємо інгредієнти на склад
    dish_ingredients = DishIngredient.query.filter_by(DishID=order_dish.DishID).all()
    for ingredient in dish_ingredients:
        product = Product.query.get(ingredient.ProductID)
        if product:
            product.Quantity += ingredient.Quantity * quantity_to_remove

    if quantity_to_remove == order_dish.Quantity:
        # If removing all, delete the order dish
        db.session.delete(order_dish)
    else:
        # Otherwise update the quantity
        order_dish.Quantity -= quantity_to_remove
    
    db.session.commit()
    
    return jsonify({'message': 'Страву видалено з замовлення'})

@bp.route('/orders/<int:order_id>/pay', methods=['POST'])
@login_required
def pay_order(order_id):
    order = Order.query.get_or_404(order_id)
    payment_method_id = request.form.get('payment_method_id')

    # Не можна оплатити скасоване замовлення
    cancel_status = OrderStatus.query.filter_by(StatusName='Скасовано').first()
    if cancel_status and order.OrderStatusID == cancel_status.OrderStatusID:
        return jsonify({'error': 'Не можна оплатити скасоване замовлення'})

    if not payment_method_id:
        return jsonify({'error': 'Необхідно вибрати спосіб оплати'})

    order.PaymentMethodID = payment_method_id
    order.PaidDateTime = datetime.utcnow()

    # Додаємо до TotalRevenue зміни тільки при оплаті
    if order.ShiftID:
        shift = Shift.query.get(order.ShiftID)
        if shift:
            if not shift.TotalRevenue:
                shift.TotalRevenue = 0
            shift.TotalRevenue += order.TotalAmount

    # Update table status if it's a table order
    if order.TableID:
        table = CafeTable.query.get(order.TableID)
        free_status = TableStatus.query.filter_by(StatusName='Вільний').first()
        table.TableStatusID = free_status.TableStatusID
        # Update seat statuses
        for seat in table.seats:
            free_seat_status = SeatStatus.query.filter_by(StatusName='Вільне').first()
            seat.SeatStatusID = free_seat_status.SeatStatusID

    db.session.commit()
    return jsonify({'message': 'Замовлення оплачено'})

@bp.route('/orders/<int:order_id>/change_status', methods=['POST'])
@login_required
def change_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status_id = int(request.form.get('status_id'))
    new_status = OrderStatus.query.get(new_status_id)
    if not new_status:
        return jsonify({'success': False, 'error': 'Статус не знайдено'})

    if new_status.StatusName == 'Скасовано':
        if not order.PaidDateTime:
            # Повертаємо інгредієнти на склад
            for order_dish in order.dishes:
                dish_ingredients = DishIngredient.query.filter_by(DishID=order_dish.DishID).all()
                for ingredient in dish_ingredients:
                    product = Product.query.get(ingredient.ProductID)
                    if product:
                        product.Quantity += ingredient.Quantity * order_dish.Quantity
            OrderDish.query.filter_by(OrderID=order.OrderID).delete()
            Payment.query.filter_by(OrderID=order.OrderID).delete()
            if order.TableID:
                table = CafeTable.query.get(order.TableID)
                free_status = TableStatus.query.filter_by(StatusName='Вільний').first()
                table.TableStatusID = free_status.TableStatusID
            db.session.delete(order)
            db.session.commit()
            return jsonify({'success': True, 'deleted': True})
        else:
            # Якщо оплачено — не дозволяємо скасувати
            return jsonify({'success': False, 'error': 'Не можна скасувати вже оплачене замовлення'})
    else:
        order.OrderStatusID = new_status_id
        db.session.commit()
        return jsonify({'success': True, 'deleted': False}) 