from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Будь ласка, увійдіть для доступу до цієї сторінки.'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes import auth, main, menu, orders, products, shifts, halls, suppliers, reports, customers, admin, api
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(menu.bp)
    app.register_blueprint(orders.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(shifts.bp)
    app.register_blueprint(halls.bp)
    app.register_blueprint(suppliers.bp)
    app.register_blueprint(reports.bp)
    app.register_blueprint(customers.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(api.bp)

    return app 