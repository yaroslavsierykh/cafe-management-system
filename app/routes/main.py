from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Order, Dish, Employee, Shift, OrderDish
from sqlalchemy import func
from datetime import datetime, timedelta
from app import db

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    """Show dashboard"""
    # Get current user's shift
    current_shift = current_user.current_shift
    if current_shift:
        shift_orders = Order.query.filter_by(ShiftID=current_shift.ShiftID)
        orders_count = shift_orders.count()
        revenue = sum(order.TotalAmount for order in shift_orders.all())
        average_check = round(revenue / orders_count, 2) if orders_count > 0 else 0
    else:
        orders_count = 0
        revenue = 0
        average_check = 0

    shift_stats = {
        'orders_count': orders_count,
        'revenue': revenue,
        'average_check': average_check
    }

    # Get top dishes for current shift
    if current_shift:
        top_dishes = db.session.query(
            Dish.DishName.label('name'),
            func.sum(OrderDish.Quantity).label('count')
        ).join(OrderDish).join(Order).filter(
            Order.ShiftID == current_shift.ShiftID
        ).group_by(Dish.DishID).order_by(
            func.sum(OrderDish.Quantity).desc()
        ).limit(5).all()
    else:
        top_dishes = []

    # Get active employees
    active_employees = Employee.query.join(Shift).filter(
        Shift.CloseDateTime.is_(None)
    ).all()

    return render_template('main/index.html',
                         shift_stats=shift_stats,
                         current_shift=current_shift,
                         top_dishes=top_dishes,
                         active_employees=active_employees,
                         now=datetime.now()) 