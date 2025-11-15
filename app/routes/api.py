from flask import Blueprint, jsonify, request
from app.models import Hall, CafeTable, TableStatus, Customer, Person, Address, Street, StreetType, Contact, Building, Unit, RoomType, Seat, SeatStatus
from app import db

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/halls/<int:hall_id>/tables')
def get_hall_tables(hall_id):
    """Get all tables for a specific hall"""
    tables = CafeTable.query.filter_by(HallID=hall_id).all()
    return jsonify({
        'tables': [{
            'TableID': table.TableID,
            'TableName': table.TableName,
            'SeatsCount': table.SeatsCount,
            'status': {
                'StatusName': table.status.StatusName
            }
        } for table in tables]
    })

@bp.route('/customers/<int:customer_id>/addresses')
def get_customer_addresses(customer_id):
    """Get all addresses (без фільтрації по клієнту)"""
    addresses = Address.query.all()
    return jsonify({
        'addresses': [{
            'AddressID': address.AddressID,
            'street': {
                'StreetName': address.unit.building.street.StreetName,
                'type': {
                    'TypeName': address.unit.building.street.type.TypeName
                }
            },
            'building': {
                'BuildingNumber': address.unit.building.BuildingNumber
            },
            'unit': {
                'UnitNumber': address.unit.UnitNumber if address.unit else None
            }
        } for address in addresses]
    })

@bp.route('/customers/new', methods=['POST'])
def new_customer():
    """Create a new customer"""
    try:
        customer_type = request.form.get('customer_type')
        if customer_type == 'person':
            person = Person(
                LastName=request.form.get('last_name'),
                FirstName=request.form.get('first_name'),
                Patronymic=request.form.get('patronymic')
            )
            db.session.add(person)
            db.session.flush()
            # Додаємо контакти
            if request.form.get('phone'):
                contact_phone = Contact(
                    PersonID=person.PersonID,
                    ContactType='Phone',
                    ContactValue=request.form.get('phone')
                )
                db.session.add(contact_phone)
            if request.form.get('email'):
                contact_email = Contact(
                    PersonID=person.PersonID,
                    ContactType='Email',
                    ContactValue=request.form.get('email')
                )
                db.session.add(contact_email)
            customer = Customer(
                PersonID=person.PersonID
            )
        else:
            person = Person(
                LastName=request.form.get('company_name'),
                FirstName='',
                Patronymic=''
            )
            db.session.add(person)
            db.session.flush()
            if request.form.get('phone'):
                contact_phone = Contact(
                    PersonID=person.PersonID,
                    ContactType='Phone',
                    ContactValue=request.form.get('phone')
                )
                db.session.add(contact_phone)
            if request.form.get('email'):
                contact_email = Contact(
                    PersonID=person.PersonID,
                    ContactType='Email',
                    ContactValue=request.form.get('email')
                )
                db.session.add(contact_email)
            customer = Customer(
                PersonID=person.PersonID
            )
        db.session.add(customer)
        db.session.commit()
        return jsonify({
            'success': True,
            'customer_id': customer.CustomerID,
            'customer_name': person.LastName if customer_type == 'company' else person.FullName
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@bp.route('/addresses/new', methods=['POST'])
def new_address():
    """Create a new address (без customer_id)"""
    try:
        unit_id = request.form.get('unit_id')
        comment = request.form.get('comment')
        address = Address(
            UnitID=unit_id,
            Comment=comment
        )
        db.session.add(address)
        db.session.commit()
        # Формуємо текст адреси для відображення
        unit = address.unit
        building = unit.building if unit else None
        street = building.street if building else None
        address_text = ''
        if street:
            address_text += f"{street.type.TypeName} {street.StreetName}, "
        if building:
            address_text += f"{building.BuildingNumber}"
        if unit:
            address_text += f", {unit.UnitNumber}"
        if comment:
            address_text += f" ({comment})"
        return jsonify({
            'success': True,
            'address_id': address.AddressID,
            'address_text': address_text
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@bp.route('/addresses')
def get_addresses():
    addresses = Address.query.all()
    return jsonify({
        'addresses': [{
            'AddressID': address.AddressID,
            'street': {
                'StreetName': address.unit.building.street.StreetName,
                'type': {
                    'TypeName': address.unit.building.street.type.TypeName
                }
            },
            'building': {
                'BuildingNumber': address.unit.building.BuildingNumber
            },
            'unit': {
                'UnitNumber': address.unit.UnitNumber if address.unit else None
            }
        } for address in addresses]
    })

@bp.route('/street_types')
def get_street_types():
    types = StreetType.query.all()
    return jsonify({
        'street_types': [{
            'StreetTypeID': t.StreetTypeID,
            'TypeName': t.TypeName
        } for t in types]
    })

@bp.route('/streets')
def get_streets_all():
    streets = Street.query.all()
    return jsonify({
        'streets': [{
            'StreetID': street.StreetID,
            'StreetName': street.StreetName,
            'type': {
                'TypeName': street.type.TypeName
            }
        } for street in streets]
    })

@bp.route('/units/get_or_create')
def get_or_create_unit():
    street_id = request.args.get('street_id')
    building_number = request.args.get('building_number')
    unit_number = request.args.get('unit_number')
    if not street_id or not building_number:
        return jsonify({'success': False, 'error': 'Необхідно вказати вулицю та будинок'})
    # Знаходимо або створюємо будинок
    building = Building.query.filter_by(StreetID=street_id, BuildingNumber=building_number).first()
    if not building:
        building = Building(StreetID=street_id, BuildingNumber=building_number)
        db.session.add(building)
        db.session.flush()
    # Знаходимо або створюємо unit
    unit = Unit.query.filter_by(BuildingID=building.BuildingID, UnitNumber=unit_number or '').first()
    if not unit:
        # Для RoomTypeID можна взяти перший доступний тип або 1
        room_type = RoomType.query.first()
        unit = Unit(BuildingID=building.BuildingID, RoomTypeID=room_type.RoomTypeID if room_type else 1, UnitNumber=unit_number or '')
        db.session.add(unit)
        db.session.flush()
    return jsonify({'success': True, 'unit_id': unit.UnitID})

@bp.route('/addresses/all')
def get_all_addresses():
    """Get all addresses (без фільтрації)"""
    addresses = Address.query.all()
    return jsonify({
        'addresses': [{
            'AddressID': address.AddressID,
            'street': {
                'StreetName': address.unit.building.street.StreetName,
                'type': {
                    'TypeName': address.unit.building.street.type.TypeName
                }
            },
            'building': {
                'BuildingNumber': address.unit.building.BuildingNumber
            },
            'unit': {
                'UnitNumber': address.unit.UnitNumber if address.unit else None
            }
        } for address in addresses]
    })

@bp.route('/halls/new', methods=['POST'])
def new_hall():
    try:
        name = request.form.get('name')
        notes = request.form.get('notes')
        
        hall = Hall(Name=name, Notes=notes)
        db.session.add(hall)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/halls/edit', methods=['POST'])
def edit_hall():
    try:
        hall_id = request.form.get('hall_id')
        name = request.form.get('name')
        notes = request.form.get('notes')
        
        hall = Hall.query.get_or_404(hall_id)
        hall.Name = name
        hall.Notes = notes
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/halls/delete/<int:hall_id>', methods=['POST'])
def delete_hall(hall_id):
    try:
        hall = Hall.query.get_or_404(hall_id)
        
        # Delete all tables and their seats first
        for table in hall.tables:
            Seat.query.filter_by(TableID=table.TableID).delete()
            db.session.delete(table)
        
        db.session.delete(hall)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/tables/new', methods=['POST'])
def new_table():
    try:
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
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/tables/edit', methods=['POST'])
def edit_table():
    try:
        table_id = request.form.get('table_id')
        name = request.form.get('name')
        seats_count = request.form.get('seats_count', type=int)
        
        table = CafeTable.query.get_or_404(table_id)
        table.TableName = name
        table.SeatsCount = seats_count
        
        # Update seats
        current_seats = Seat.query.filter_by(TableID=table.TableID).all()
        current_seat_count = len(current_seats)
        new_seat_count = seats_count
        
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
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/tables/delete/<int:table_id>', methods=['POST'])
def delete_table(table_id):
    try:
        table = CafeTable.query.get_or_404(table_id)
        
        # Delete all seats first
        Seat.query.filter_by(TableID=table_id).delete()
        
        # Delete the table
        db.session.delete(table)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}) 