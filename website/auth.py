import bcrypt
from functools import wraps
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user, LoginManager,UserMixin
from . import db   # from __init__.py import db
from .models import User

auth = Blueprint('auth', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        if not getattr(current_user, 'is_admin', False):
            flash('You are not authorized to access this page!', 'danger')
            return redirect(url_for('/'))  # Adjust the redirect URL as needed
        return f(*args, **kwargs)
    return decorated_function

# Route to Open & Register SignUp Form via Admin Login
@auth.route('/signup', methods=['GET', 'POST'])
@admin_required
def signup():
    
    if request.method == 'GET':
        active_page = 'signup'
        title = "Sign Up"
        return render_template('signup.html', title = title, active_page = active_page)

    if request.method == 'POST':
        username = request.form['inputName']
        email = request.form['inputEmail']
        password = request.form['inputPassword']
        user_level = request.form['inputLevel']

        # Create a new user instance
        new_user = User(username=username, email=email, password='', user_level=user_level)
        new_user.set_password(password)  # Hash the password

        cursor = db.connection.cursor()
        insert_query = "INSERT INTO users (user_name, user_email, user_password, user_level) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (new_user.username, new_user.email, new_user.password, new_user.user_level))
        db.connection.commit()
        cursor.close()

        flash('User registered successfully!', 'success')
        return redirect(url_for('auth.login'))
    else:
        flash('User registration Failed!', 'danger')
        return render_template('signup.html', title = "Sign Up")

# Route for Login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    active_page = 'login'
    title = "Login"

    if request.method == 'POST':
        user_email = request.form['inputEmail']
        user_password = request.form['inputPassword']
        
        user = User.get_by_email(user_email)
        if user and user.check_password(user_password):
            flash('Login successful! Redirecting...', 'success')
            login_user(user) # Logs in the user and manages the session
            return redirect(url_for('auth.redirect_user_home'))
        else:
            flash('Invalid credentials!', 'danger') #(Message, Category) in the HTML
            return redirect(url_for('auth.login'))
    else:
        return render_template('login.html', title=title, active_page=active_page)

@auth.route('/redirect_user_home')
@login_required
def redirect_user_home():
    return render_template('redirect_user_home.html')

# Route for User Page after login
@auth.route('/dashBoard', methods=['GET'])
@login_required
def dashBoard():
    title = "User Home"
    username = current_user.username  # Access the current logged-in user's username
    return render_template('dashBoard.html', title = title, username = username)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))