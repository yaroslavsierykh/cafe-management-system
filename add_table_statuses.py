from app import create_app, db
from app.models import TableStatus, SeatStatus

def init_statuses():
    app = create_app()
    with app.app_context():
        # Initialize table statuses
        table_statuses = [
            {'StatusName': 'Вільний'},
            {'StatusName': 'Зайнятий'},
            {'StatusName': 'Резерв'}
        ]
        
        for status in table_statuses:
            if not TableStatus.query.filter_by(StatusName=status['StatusName']).first():
                table_status = TableStatus(**status)
                db.session.add(table_status)
        
        # Initialize seat statuses
        seat_statuses = [
            {'StatusName': 'Вільне'},
            {'StatusName': 'Зайняте'}
        ]
        
        for status in seat_statuses:
            if not SeatStatus.query.filter_by(StatusName=status['StatusName']).first():
                seat_status = SeatStatus(**status)
                db.session.add(seat_status)
        
        db.session.commit()
        print("Table and seat statuses initialized successfully!")

if __name__ == '__main__':
    init_statuses() 