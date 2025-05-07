from flask import render_template, redirect, url_for, request

from flask_login import login_user, logout_user, current_user

from app import login_manager

from .forms import LoginForm

from .services import login_user_func

from . import auth_bp

from flask import request, jsonify
from flask_jwt_extended import create_access_token


@auth_bp.route('/api/v1/token-login', methods=['POST'])
def token_login():
    username = request.json.get('username')
    password = request.json.get('password')
    from app.admin import User

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200

    return jsonify({'error': 'Invalid credentials'}), 401



@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    title = 'Login'
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))

    form = LoginForm()

    if form.validate_on_submit():
        login_user_func(form.email.data, form.password.data, form.remember_me.data)

    return render_template('auth/login.html',
                    title = title,
                    form = form,
                    login = True,
                    )


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('public.index'))


@login_manager.user_loader
def load_user(user_id):
    from app.admin import User
    return User.query.get(int(user_id))