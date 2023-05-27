from flask import  Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import db 
from .models import User
from werkzeug.security import check_password_hash, generate_password_hash

log = Blueprint('log', __name__)

@log.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username = username).first()
        
    
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                flash('Logged in!', 'success')
                return redirect(url_for('views.home'))
        flash('Username or password is incorrect.', 'error')



    return render_template('login.html', user = current_user)

@log.route('/sign-up', methods = ['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password') 
        passwordConfirm = request.form.get('passwordConfirm')
        user = User.query.filter_by(username = username).first()

        if user:
            flash('User already exists!', 'error')
        elif len(username) < 1:
            flash('Please insert your username!', 'error')
        elif len(password) < 1:
            flash('Please insert your password!', 'error')
        elif password != passwordConfirm:
            flash('Passwords do not match! Please try again.', 'error')
        else:
            newUser = User(username = username, password = generate_password_hash(password, method = 'sha256'))
            db.session.add(newUser)
            db.session.commit()
            login_user(newUser)
            flash('Account created!', 'success')
            return redirect(url_for('views.home'))



    return render_template('sign_up.html', user = current_user)


@log.route('/logout', )
def logout():
    logout_user(    )
    flash('Logged out!', 'success')
    return redirect(url_for('log.login'))