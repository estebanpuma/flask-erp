from flask import redirect,url_for,request, flash

from flask_login import login_user


def login_user_func(email, password, remember=None):

    from ..admin import User
    user = User.query.filter_by(email = email).first()

    if user:
        
        if user.check_password(password):
            
            login_user(user, remember=remember)

            next_page = request.args.get('next', None)
            
            if not next_page:
                next_page = url_for("public.index")
            
            return redirect(next_page)
        

