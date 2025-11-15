from app import create_app, db
from app.init_data import init_sample_data

def init_database():
    """Initialize the database"""
    app = create_app()
    with app.app_context():
        # Create all tables
        db.drop_all()
        db.create_all()
        
        # Initialize sample data
        init_sample_data()

if __name__ == '__main__':
    init_database() 