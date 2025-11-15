from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('customers', __name__)

@bp.route('/customers')
@login_required
def index():
    """Show list of customers"""
    return render_template('customers/index.html') 