from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app.models import Employee, Role, Hall, TableStatus, CafeTable, Seat, SeatStatus, Supplier, Contract, Delivery, DeliveryItem, Product, Order, Person
from app import db
from datetime import datetime
import decimal

bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.role or current_user.role.RoleName != 'Адміністратор':
            flash('У вас немає доступу до цієї сторінки.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/admin')
@login_required
@admin_required
def index():
    return render_template('admin/index.html')

@bp.route('/admin/employees', methods=['GET', 'POST'])
@login_required
@admin_required
def employees():
    employees = Employee.query.all()
    roles = Role.query.all()
    if request.method == 'POST':
        # Add new employee
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        patronymic = request.form.get('patronymic')
        username = request.form.get('username')
        password = request.form.get('password')
        role_id = request.form.get('role_id', type=int)
        is_active = bool(request.form.get('is_active'))
        # Create person
        person = Person(FirstName=first_name, LastName=last_name, Patronymic=patronymic)
        db.session.add(person)
        db.session.flush()  # Get PersonID
        # Create employee
        employee = Employee(
            PersonID=person.PersonID,
            UserName=username,
            RoleID=role_id,
            IsActive=is_active
        )
        employee.set_password(password)
        db.session.add(employee)
        db.session.commit()
        flash('Працівника додано', 'success')
        return redirect(url_for('admin.employees'))
    return render_template('admin/employees.html', employees=employees, roles=roles)

@bp.route('/admin/employees/<int:employee_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    roles = Role.query.all()
    if request.method == 'POST':
        # Update employee and person data
        employee.person.FirstName = request.form.get('first_name')
        employee.person.LastName = request.form.get('last_name')
        employee.person.Patronymic = request.form.get('patronymic')
        employee.UserName = request.form.get('username')
        employee.RoleID = request.form.get('role_id', type=int)
        employee.IsActive = bool(request.form.get('is_active'))
        password = request.form.get('password')
        if password:
            employee.set_password(password)
        db.session.commit()
        flash('Дані працівника оновлено', 'success')
        return redirect(url_for('admin.employees'))
    return render_template('admin/edit_employee.html', employee=employee, roles=roles)

@bp.route('/admin/employees/<int:employee_id>/toggle_active', methods=['POST'])
@login_required
@admin_required
def toggle_employee_active(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    employee.IsActive = not employee.IsActive
    db.session.commit()
    flash(f"Статус працівника змінено на {'активний' if employee.IsActive else 'неактивний'}", 'success')
    return redirect(url_for('admin.employees'))

@bp.route('/admin/halls')
@login_required
@admin_required
def halls():
    halls = Hall.query.all()
    return render_template('admin/halls.html', halls=halls)

@bp.route('/admin/halls/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_hall():
    if request.method == 'POST':
        name = request.form.get('name')
        notes = request.form.get('notes')
        
        hall = Hall(Name=name, Notes=notes)
        db.session.add(hall)
        db.session.commit()
        
        flash('Зал додано', 'success')
        return redirect(url_for('admin.halls'))
    
    return render_template('admin/new_hall.html')

@bp.route('/admin/tables')
@login_required
@admin_required
def tables():
    tables = CafeTable.query.all()
    return render_template('admin/tables.html', tables=tables)

@bp.route('/admin/tables/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_table():
    if request.method == 'POST':
        name = request.form.get('name')
        hall_id = request.form.get('hall_id')
        seats_count = request.form.get('seats_count', type=int)
        
        # Get default "Вільний" status
        free_status = TableStatus.query.filter_by(StatusName='Вільний').first()
        
        table = CafeTable(
            TableName=name,
            HallID=hall_id,
            TableStatusID=free_status.TableStatusID,
            SeatsCount=seats_count
        )
        db.session.add(table)
        db.session.commit()
        
        # Create seats for the table
        free_seat_status = SeatStatus.query.filter_by(StatusName='Вільне').first()
        for i in range(1, seats_count + 1):
            seat = Seat(
                TableID=table.TableID,
                SeatNumber=i,
                SeatStatusID=free_seat_status.SeatStatusID
            )
            db.session.add(seat)
        
        db.session.commit()
        flash('Стіл додано', 'success')
        return redirect(url_for('admin.tables'))
    
    halls = Hall.query.all()
    return render_template('admin/new_table.html', halls=halls)

@bp.route('/admin/tables/<int:table_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_table(table_id):
    table = CafeTable.query.get_or_404(table_id)
    
    if request.method == 'POST':
        table.TableName = request.form.get('name')
        table.HallID = request.form.get('hall_id')
        table.SeatsCount = request.form.get('seats_count', type=int)
        
        # Update seats
        current_seats = Seat.query.filter_by(TableID=table.TableID).all()
        current_seat_count = len(current_seats)
        new_seat_count = table.SeatsCount
        
        if new_seat_count > current_seat_count:
            # Add new seats
            free_seat_status = SeatStatus.query.filter_by(StatusName='Вільне').first()
            for i in range(current_seat_count + 1, new_seat_count + 1):
                seat = Seat(
                    TableID=table.TableID,
                    SeatNumber=i,
                    SeatStatusID=free_seat_status.SeatStatusID
                )
                db.session.add(seat)
        elif new_seat_count < current_seat_count:
            # Remove excess seats
            for seat in current_seats[new_seat_count:]:
                db.session.delete(seat)
        
        db.session.commit()
        flash('Стіл оновлено', 'success')
        return redirect(url_for('admin.tables'))
    
    halls = Hall.query.all()
    return render_template('admin/edit_table.html', table=table, halls=halls)

@bp.route('/admin/tables/<int:table_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_table(table_id):
    table = CafeTable.query.get_or_404(table_id)
    
    # Delete all seats first
    Seat.query.filter_by(TableID=table_id).delete()
    
    # Delete the table
    db.session.delete(table)
    db.session.commit()
    
    flash('Стіл видалено', 'success')
    return redirect(url_for('admin.tables'))

@bp.route('/admin/tables/<int:table_id>/change_status', methods=['POST'])
@login_required
@admin_required
def change_table_status(table_id):
    table = CafeTable.query.get_or_404(table_id)
    new_status_id = int(request.form.get('status_id'))
    new_status = TableStatus.query.get(new_status_id)
    if not new_status:
        return {'success': False, 'error': 'Статус не знайдено'}
    # Перевірка наявності неоплачених замовлень
    unpaid_orders = Order.query.filter_by(TableID=table_id, PaidDateTime=None).all()
    if unpaid_orders:
        return {'success': False, 'error': 'Неможливо змінити статус: є неоплачені замовлення'}
    table.TableStatusID = new_status_id
    db.session.commit()
    return {'success': True}

# Постачальники
@bp.route('/api/suppliers/new', methods=['POST'])
def new_supplier():
    try:
        supplier = Supplier(
            SupplierType=request.form['supplier_type'],
            CompanyName=request.form['company_name'],
            ContactPerson=request.form.get('contact_person'),
            Phone=request.form['phone'],
            Email=request.form.get('email'),
            Address=request.form.get('address'),
            TaxNumber=request.form['tax_number'],
            FOPNumber=request.form.get('fop_number') if request.form['supplier_type'] == 'FOP' else None,
            FOPRegistrationDate=datetime.strptime(request.form.get('fop_registration_date'), '%Y-%m-%d').date() if request.form.get('fop_registration_date') and request.form['supplier_type'] == 'FOP' else None,
            EDRPOU=request.form.get('edrpou') if request.form['supplier_type'] == 'TOV' else None,
            LegalForm=request.form.get('legal_form') if request.form['supplier_type'] == 'TOV' else None,
            DirectorName=request.form.get('director_name') if request.form['supplier_type'] == 'TOV' else None
        )
        db.session.add(supplier)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/api/suppliers/edit', methods=['POST'])
def edit_supplier():
    try:
        supplier = Supplier.query.get(request.form['supplier_id'])
        if not supplier:
            return jsonify({'success': False, 'error': 'Постачальник не знайдений'})
        
        supplier.SupplierType = request.form['supplier_type']
        supplier.CompanyName = request.form['company_name']
        supplier.ContactPerson = request.form.get('contact_person')
        supplier.Phone = request.form['phone']
        supplier.Email = request.form.get('email')
        supplier.Address = request.form.get('address')
        supplier.TaxNumber = request.form['tax_number']
        
        if request.form['supplier_type'] == 'FOP':
            supplier.FOPNumber = request.form.get('fop_number')
            supplier.FOPRegistrationDate = datetime.strptime(request.form.get('fop_registration_date'), '%Y-%m-%d').date() if request.form.get('fop_registration_date') else None
            supplier.EDRPOU = None
            supplier.LegalForm = None
            supplier.DirectorName = None
        else:
            supplier.FOPNumber = None
            supplier.FOPRegistrationDate = None
            supplier.EDRPOU = request.form.get('edrpou')
            supplier.LegalForm = request.form.get('legal_form')
            supplier.DirectorName = request.form.get('director_name')
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/api/suppliers/delete/<int:supplier_id>', methods=['POST'])
def delete_supplier(supplier_id):
    try:
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return jsonify({'success': False, 'error': 'Постачальник не знайдений'})
        
        # Видаляємо всі контракти та поставки постачальника
        contracts = Contract.query.filter_by(SupplierID=supplier_id).all()
        for contract in contracts:
            deliveries = Delivery.query.filter_by(ContractID=contract.ContractID).all()
            for delivery in deliveries:
                DeliveryItem.query.filter_by(DeliveryID=delivery.DeliveryID).delete()
            Delivery.query.filter_by(ContractID=contract.ContractID).delete()
        Contract.query.filter_by(SupplierID=supplier_id).delete()
        
        db.session.delete(supplier)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

# Контракти
@bp.route('/api/contracts/new', methods=['POST'])
def new_contract():
    try:
        contract = Contract(
            SupplierID=request.form['supplier_id'],
            ContractNumber=request.form['contract_number'],
            StartDate=datetime.strptime(request.form['start_date'], '%Y-%m-%d'),
            EndDate=datetime.strptime(request.form['end_date'], '%Y-%m-%d') if request.form.get('end_date') else None,
            Description=request.form.get('description'),
            TotalValue=float(request.form['total_value']),
            PaymentTerms=request.form.get('payment_terms'),
            DeliveryTerms=request.form.get('delivery_terms')
        )
        db.session.add(contract)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/api/contracts/edit', methods=['POST'])
def edit_contract():
    try:
        contract = Contract.query.get(request.form['contract_id'])
        if not contract:
            return jsonify({'success': False, 'error': 'Контракт не знайдений'})
        
        contract.SupplierID = request.form['supplier_id']
        contract.ContractNumber = request.form['contract_number']
        contract.StartDate = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        contract.EndDate = datetime.strptime(request.form['end_date'], '%Y-%m-%d') if request.form.get('end_date') else None
        contract.Description = request.form.get('description')
        contract.TotalValue = float(request.form['total_value'])
        contract.PaymentTerms = request.form.get('payment_terms')
        contract.DeliveryTerms = request.form.get('delivery_terms')
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/api/contracts/delete/<int:contract_id>', methods=['POST'])
def delete_contract(contract_id):
    try:
        contract = Contract.query.get(contract_id)
        if not contract:
            return jsonify({'success': False, 'error': 'Контракт не знайдений'})
        
        # Видаляємо всі поставки контракту
        deliveries = Delivery.query.filter_by(ContractID=contract_id).all()
        for delivery in deliveries:
            DeliveryItem.query.filter_by(DeliveryID=delivery.DeliveryID).delete()
        Delivery.query.filter_by(ContractID=contract_id).delete()
        
        db.session.delete(contract)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

# Поставки
@bp.route('/api/deliveries/new', methods=['POST'])
def new_delivery():
    try:
        contract = Contract.query.get(request.form['contract_id'])
        if not contract:
            return jsonify({'success': False, 'error': 'Контракт не знайдений'})
        # Додаткові перевірки
        if hasattr(contract, 'Status') and contract.Status and contract.Status.lower() in ['завершено', 'закрито', 'неактивний']:
            return jsonify({'success': False, 'error': 'Контракт завершено або неактивний, нові поставки неможливі'})
        if hasattr(contract, 'EndDate') and contract.EndDate and contract.EndDate < datetime.utcnow().date():
            return jsonify({'success': False, 'error': 'Контракт завершено за датою, нові поставки неможливі'})
        if hasattr(contract, 'IsActive') and contract.IsActive is False:
            return jsonify({'success': False, 'error': 'Контракт неактивний, нові поставки неможливі'})
        # Підрахунок суми вже існуючих поставок
        existing_deliveries = Delivery.query.filter_by(ContractID=contract.ContractID).all()
        existing_sum = sum([d.TotalAmount or 0 for d in existing_deliveries])
        # Підрахунок суми нової поставки
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        unit_prices = request.form.getlist('unit_price[]')
        new_delivery_sum = 0
        for i in range(len(product_ids)):
            quantity = decimal.Decimal(quantities[i])
            unit_price = decimal.Decimal(unit_prices[i])
            new_delivery_sum += quantity * unit_price
        if contract.TotalValue is not None and (existing_sum + new_delivery_sum) > contract.TotalValue:
            return jsonify({'success': False, 'error': f'Сума всіх поставок ({existing_sum + new_delivery_sum}) перевищує суму контракту ({contract.TotalValue})'})
        # (Опціонально) Заборонити нову поставку, якщо є незавершена
        if any(d.Status == 'pending' for d in existing_deliveries):
            return jsonify({'success': False, 'error': 'Є незавершена поставка за цим контрактом. Завершіть її перед створенням нової.'})
        # Далі стандартна логіка створення поставки
        delivery = Delivery(
            ContractID=contract.ContractID,
            SupplierID=contract.SupplierID,
            DeliveryDate=datetime.strptime(request.form['delivery_date'], '%Y-%m-%dT%H:%M'),
            Notes=request.form.get('notes'),
            Status='pending',
            TotalAmount=0
        )
        db.session.add(delivery)
        db.session.flush()  # Отримуємо DeliveryID
        total_amount = 0
        for i in range(len(product_ids)):
            product = Product.query.get(product_ids[i])
            if not product:
                raise Exception(f'Товар з ID {product_ids[i]} не знайдений')
            quantity = decimal.Decimal(quantities[i])
            unit_price = decimal.Decimal(unit_prices[i])
            total_price = quantity * unit_price
            item = DeliveryItem(
                DeliveryID=delivery.DeliveryID,
                ProductID=product.ProductID,
                Quantity=quantity,
                UnitPrice=unit_price,
                TotalPrice=total_price
            )
            db.session.add(item)
            total_amount += total_price
            product.Quantity += quantity
        delivery.TotalAmount = total_amount
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/api/deliveries/<int:delivery_id>')
def get_delivery(delivery_id):
    try:
        delivery = Delivery.query.get(delivery_id)
        if not delivery:
            return jsonify({'success': False, 'error': 'Поставка не знайдена'})
        
        items = DeliveryItem.query.filter_by(DeliveryID=delivery_id).all()
        items_data = []
        for item in items:
            product = Product.query.get(item.ProductID)
            items_data.append({
                'product': {
                    'ProductID': product.ProductID,
                    'ProductName': product.ProductName
                },
                'Quantity': item.Quantity,
                'UnitPrice': item.UnitPrice,
                'TotalPrice': item.TotalPrice
            })
        
        return jsonify({
            'success': True,
            'delivery': {
                'DeliveryID': delivery.DeliveryID,
                'DeliveryDate': delivery.DeliveryDate.isoformat(),
                'Status': delivery.Status,
                'TotalAmount': delivery.TotalAmount,
                'Notes': delivery.Notes,
                'contract': {
                    'ContractID': delivery.contract.ContractID,
                    'ContractNumber': delivery.contract.ContractNumber
                },
                'supplier': {
                    'SupplierID': delivery.contract.supplier.SupplierID,
                    'CompanyName': delivery.contract.supplier.CompanyName
                },
                'items': items_data
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/api/deliveries/<int:delivery_id>/complete', methods=['POST'])
def complete_delivery(delivery_id):
    try:
        delivery = Delivery.query.get(delivery_id)
        if not delivery:
            return jsonify({'success': False, 'error': 'Поставка не знайдена'})
        
        if delivery.Status != 'pending':
            return jsonify({'success': False, 'error': 'Поставка вже завершена або скасована'})
        
        delivery.Status = 'delivered'
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/admin/contracts')
@login_required
@admin_required
def contracts():
    suppliers = Supplier.query.all()
    contracts = Contract.query.all()
    deliveries = Delivery.query.order_by(Delivery.DeliveryDate.desc()).limit(10).all()
    products = Product.query.all()
    return render_template('admin/contracts.html', suppliers=suppliers, contracts=contracts, deliveries=deliveries, products=products)

@bp.route('/admin/contracts/<int:contract_id>')
@login_required
@admin_required
def contract_detail(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    supplier = Supplier.query.get(contract.SupplierID)
    deliveries = Delivery.query.filter_by(ContractID=contract_id).order_by(Delivery.DeliveryDate.desc()).all()
    items = []
    for delivery in deliveries:
        delivery_items = DeliveryItem.query.filter_by(DeliveryID=delivery.DeliveryID).all()
        for item in delivery_items:
            product = Product.query.get(item.ProductID)
            items.append({
                'delivery': delivery,
                'item': item,
                'product': product
            })
    return render_template('admin/contract_detail.html', contract=contract, supplier=supplier, deliveries=deliveries, items=items) 