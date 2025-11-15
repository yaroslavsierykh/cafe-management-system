from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import Employee, Person, Role, Contact
from app import db
from werkzeug.security import check_password_hash

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = Employee.query.filter_by(UserName=username).first()
        
        if user and check_password_hash(user.PasswordHash, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        
        flash('Невірний логін або пароль', 'danger')
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if not current_user.role.RoleName == 'Адміністратор':
        flash('Доступ заборонено', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        patronymic = request.form.get('patronymic')
        username = request.form.get('username')
        password = request.form.get('password')
        role_id = request.form.get('role_id')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        if Employee.query.filter_by(UserName=username).first():
            flash('Користувач з таким іменем вже існує', 'danger')
            return redirect(url_for('auth.register'))
        
        person = Person(
            FirstName=first_name,
            LastName=last_name,
            Patronymic=patronymic
        )
        db.session.add(person)
        db.session.flush()
        
        # Додаємо контакти
        if email:
            contact_email = Contact(
                PersonID=person.PersonID,
                ContactType='Email',
                ContactValue=email
            )
            db.session.add(contact_email)
        if phone:
            contact_phone = Contact(
                PersonID=person.PersonID,
                ContactType='Phone',
                ContactValue=phone
            )
            db.session.add(contact_phone)
        
        employee = Employee(
            PersonID=person.PersonID,
            UserName=username,
            RoleID=role_id,
            IsActive=True
        )
        employee.set_password(password)
        
        db.session.add(employee)
        db.session.commit()
        
        flash('Працівника успішно зареєстровано', 'success')
        return redirect(url_for('main.index'))
    
    roles = Role.query.all()
    return render_template('auth/register.html', roles=roles) 