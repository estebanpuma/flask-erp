from flask import render_template, redirect, url_for, request

from flask_login import login_user, logout_user, current_user

from app import login_manager

from .forms import LoginForm

from .services import login_user_func

from . import auth_bp


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