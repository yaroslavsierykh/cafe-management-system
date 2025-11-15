from app import create_app, db
from app.models import PaymentMethod

app = create_app()
with app.app_context():
    # Add payment methods
    payment_methods = [
        PaymentMethod(MethodName='Готівка'),
        PaymentMethod(MethodName='Картка'),
        PaymentMethod(MethodName='Безготівковий')
    ]
    
    db.session.add_all(payment_methods)
    db.session.commit()
    
    # Print added methods
    print('Added payment methods:')
    for pm in PaymentMethod.query.all():
        print(f'- {pm.MethodName}') 