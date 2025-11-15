from app import db, create_app
from app.models import Hall, TableStatus, CafeTable, SeatStatus, Seat

def add_halls_and_tables():
    app = create_app()
    with app.app_context():
        # Get or create table statuses
        free_status = TableStatus.query.filter_by(StatusName='Вільний').first()
        if not free_status:
            free_status = TableStatus(StatusName='Вільний')
            db.session.add(free_status)
            db.session.commit()

        # Get or create seat status
        free_seat_status = SeatStatus.query.filter_by(StatusName='Вільне').first()
        if not free_seat_status:
            free_seat_status = SeatStatus(StatusName='Вільне')
            db.session.add(free_seat_status)
            db.session.commit()

        # Create first hall
        hall1 = Hall(Name='Основний зал', Notes='Основний зал ресторану')
        db.session.add(hall1)
        db.session.commit()

        # Add tables to first hall
        tables_hall1 = [
            ('Стіл 1', 4),
            ('Стіл 2', 4),
            ('Стіл 3', 2),
            ('Стіл 4', 6),
            ('Стіл 5', 2)
        ]

        for table_name, seats in tables_hall1:
            table = CafeTable(
                TableName=table_name,
                HallID=hall1.HallID,
                TableStatusID=free_status.TableStatusID,
                SeatsCount=seats
            )
            db.session.add(table)
            db.session.commit()

            # Create seats for the table
            for i in range(1, seats + 1):
                seat = Seat(
                    TableID=table.TableID,
                    SeatNumber=i,
                    SeatStatusID=free_seat_status.SeatStatusID
                )
                db.session.add(seat)
            db.session.commit()

        # Create second hall
        hall2 = Hall(Name='VIP зал', Notes='Закритий зал для особливих подій')
        db.session.add(hall2)
        db.session.commit()

        # Add tables to second hall
        tables_hall2 = [
            ('VIP Стіл 1', 8),
            ('VIP Стіл 2', 6),
            ('VIP Стіл 3', 4)
        ]

        for table_name, seats in tables_hall2:
            table = CafeTable(
                TableName=table_name,
                HallID=hall2.HallID,
                TableStatusID=free_status.TableStatusID,
                SeatsCount=seats
            )
            db.session.add(table)
            db.session.commit()

            # Create seats for the table
            for i in range(1, seats + 1):
                seat = Seat(
                    TableID=table.TableID,
                    SeatNumber=i,
                    SeatStatusID=free_seat_status.SeatStatusID
                )
                db.session.add(seat)
            db.session.commit()

        print("Halls and tables have been added successfully!")

if __name__ == '__main__':
    add_halls_and_tables() 