from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('reports', __name__)

@bp.route('/reports')
@login_required
def index():
    """Show reports dashboard"""
    return render_template('reports/index.html') 