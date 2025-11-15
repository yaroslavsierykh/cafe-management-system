from flask import Blueprint, render_template, request, flash, redirect, url_for, make_response, send_file
from flask_login import login_required, current_user
from app.models import Shift, Employee, Order, OrderStatus
from app import db
from datetime import datetime
import io
import openpyxl
from openpyxl.styles import Font

bp = Blueprint('shifts', __name__)

@bp.route('/shifts')
@login_required
def index():
    """Show list of shifts"""
    shifts = Shift.query.order_by(Shift.OpenDateTime.desc()).all()
    return render_template('shifts/index.html', shifts=shifts)

@bp.route('/shifts/open', methods=['POST'])
@login_required
def open_shift():
    """Open a new shift"""
    # Заборонити відкривати нову зміну, якщо у будь-кого є відкрита зміна
    if Shift.query.filter_by(CloseDateTime=None).first():
        flash('Вже є відкрита зміна. Спочатку закрийте її.', 'warning')
        return redirect(url_for('main.index'))
    if current_user.current_shift:
        flash('У вас вже є активна зміна', 'warning')
        return redirect(url_for('main.index'))
    description = request.form.get('description')
    shift = Shift(
        EmployeeID=current_user.EmployeeID,
        OpenDateTime=datetime.now(),
        Notes=description
    )
    db.session.add(shift)
    db.session.commit()
    flash('Зміну успішно відкрито', 'success')
    return redirect(url_for('main.index'))

@bp.route('/shifts/close', methods=['POST'])
@login_required
def close_shift():
    """Close current shift"""
    shift = current_user.current_shift
    if not shift:
        flash('У вас немає активної зміни', 'warning')
        return redirect(url_for('main.index'))
    # Перевірка на неоплачені замовлення, ігноруючи скасовані
    unpaid_orders = [order for order in shift.orders if order.PaidDateTime is None and (not order.status or order.status.StatusName != 'Скасовано')]
    if unpaid_orders:
        ids = ', '.join(str(order.OrderID) for order in unpaid_orders)
        flash(f'Неможливо закрити зміну: є неоплачені замовлення! (ID: {ids})', 'danger')
        return redirect(url_for('main.index'))
    shift.CloseDateTime = datetime.now()
    db.session.commit()
    flash('Зміну успішно закрито', 'success')
    return redirect(url_for('main.index'))

@bp.route('/shifts/report')
@login_required
def report():
    """Show shifts report with filters and detailed dish sales"""
    from_date = request.args.get('from_date', datetime.now().date().isoformat())
    to_date = request.args.get('to_date', datetime.now().date().isoformat())
    employee_id = request.args.get('employee_id', type=int)
    query = Shift.query
    if from_date:
        query = query.filter(Shift.OpenDateTime >= from_date)
    if to_date:
        query = query.filter(Shift.OpenDateTime <= to_date + ' 23:59:59')
    if employee_id:
        query = query.filter_by(EmployeeID=employee_id)
    shifts = query.order_by(Shift.OpenDateTime.desc()).all()
    employees = Employee.query.filter_by(IsActive=True).all()
    # Додаємо деталізацію по стравам для кожної зміни
    shift_dishes = {}
    for shift in shifts:
        dish_stats = {}
        for order in shift.orders:
            if not order.PaidDateTime:
                continue
            for od in order.dishes:
                dish_id = od.DishID
                if dish_id not in dish_stats:
                    dish_stats[dish_id] = {
                        'dish': od.dish,
                        'quantity': 0,
                        'total': 0
                    }
                dish_stats[dish_id]['quantity'] += od.Quantity
                dish_stats[dish_id]['total'] += float(od.PriceAtTime) * od.Quantity
        shift_dishes[shift.ShiftID] = dish_stats
    return render_template('shifts/report.html',
                         shifts=shifts,
                         employees=employees,
                         from_date=from_date,
                         to_date=to_date,
                         selected_employee=employee_id,
                         shift_dishes=shift_dishes)

@bp.route('/shifts/<int:shift_id>/report_xlsx')
@login_required
def report_xlsx(shift_id):
    shift = Shift.query.get_or_404(shift_id)
    dish_stats = {}
    for order in shift.orders:
        if not order.PaidDateTime:
            continue
        for od in order.dishes:
            dish_id = od.DishID
            if dish_id not in dish_stats:
                dish_stats[dish_id] = {
                    'dish': od.dish,
                    'quantity': 0,
                    'total': 0
                }
            dish_stats[dish_id]['quantity'] += od.Quantity
            dish_stats[dish_id]['total'] += float(od.PriceAtTime) * od.Quantity
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f'Зміна {shift.ShiftID}'
    ws.append([f'Звіт по зміні #{shift.ShiftID}'])
    ws.append([f'Працівник:', f'{shift.employee.person.LastName} {shift.employee.person.FirstName}'])
    ws.append([f'Відкрито:', shift.OpenDateTime.strftime('%d.%m.%Y %H:%M')])
    ws.append([f'Закрито:', shift.CloseDateTime.strftime('%d.%m.%Y %H:%M') if shift.CloseDateTime else 'Відкрита'])
    ws.append([f'Опис:', shift.Notes or '-'])
    ws.append([])
    ws.append(['Страва', 'Кількість', 'Сума', 'Рецепт'])
    for cell in ws[7]:
        cell.font = Font(bold=True)
    for d in dish_stats.values():
        recipe = '\n'.join([
            f"{ing.product.ProductName} — {int(ing.Quantity) if ing.Quantity == int(ing.Quantity) else ing.Quantity} {ing.product.measurement_unit.UnitName}"
            for ing in d['dish'].ingredients
        ]) or '(немає інгредієнтів)'
        ws.append([
            d['dish'].DishName,
            d['quantity'],
            round(d['total'], 2),
            recipe
        ])
    ws.append([])
    ws.append(['Всього страв продано:', sum(d['quantity'] for d in dish_stats.values())])
    ws.append(['Загальна сума:', round(sum(d['total'] for d in dish_stats.values()), 2)])
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name=f'shift_report_{shift.ShiftID}.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') 