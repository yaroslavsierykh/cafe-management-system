from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('suppliers', __name__)

@bp.route('/suppliers')
@login_required
def index():
    """Show list of suppliers"""
    return render_template('suppliers/index.html') 