from flask import Blueprint

# Import all blueprints
from .auth import bp as auth_bp
from .admin import bp as admin_bp
from .shifts import bp as shifts_bp
from .menu import bp as menu_bp
from .products import bp as products_bp
from .halls import bp as halls_bp
from .orders import bp as orders_bp
from .customers import bp as customers_bp
from .suppliers import bp as suppliers_bp
from .reports import bp as reports_bp
from .main import bp as main_bp

# List of all blueprints to register
blueprints = [
    main_bp,      # Main pages (dashboard, etc.)
    auth_bp,      # Authentication and user management
    admin_bp,     # Administrative functions
    shifts_bp,    # Work shifts management
    menu_bp,      # Menu and dishes management
    products_bp,  # Products and ingredients
    halls_bp,     # Halls and tables management
    orders_bp,    # Orders and service
    customers_bp, # Customers and addresses
    suppliers_bp, # Suppliers and contracts
    reports_bp    # Analytics and reports
] 