import bcrypt
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user, LoginManager,UserMixin
from . import db   # from __init__.py import db
from .models import User

auth = Blueprint('auth', __name__)

# Route to Open & Register SignUp Form
@auth.route('/signup', methods=['GET', 'POST'])
@login_required
def signup():
    # Ensure only admin can access this page
    if not current_user.is_admin:
        flash('You are not authorized to access this page!', 'danger')
        return redirect(url_for('auth.login'))  # Redirect to a safe page or home
    
    if request.method == 'GET':
        active_page = 'signup'
        title = "Sign Up"
        return render_template('signup.html', title=title, active_page=active_page)

    # POST method
    if request.method == 'POST':
        user_name = request.form['inputName']
        user_email = request.form['inputEmail']
        user_password = request.form['inputPassword']
        user_level = request.form['inputLevel']
        
        # hashed_password = bcrypt.generate_password_hash(user_password).decode('utf-8')
        hashed_password = generate_password_hash(user_password)
        # Creating the cursor object for executing SQL queries with the connected MySQL database
        con = db.connection.cursor()

        insert = "INSERT INTO users (user_name, user_email, user_password, user_level) VALUES (%s, %s, %s, %s)"
        con.execute(insert, (user_name, user_email, hashed_password, user_level))
        db.connection.commit()
        con.close()
        
        flash('User registered successfully!', 'success')
        return redirect(url_for('auth.login'))
    else:
        return render_template('signup.html', title="Sign Up")

# Route for Login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    active_page = 'login'
    title = "Login"

    if request.method == 'POST':
        user_email = request.form['inputEmail']
        user_password = request.form['inputPassword']

        user = User.get_by_email(user_email)

        if user and check_password_hash(user.password, user_password):
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
@auth.route('/userHome', methods=['GET'])
@login_required
def userHome():
    title = "User Home"
    username = current_user.username  # Access the current logged-in user's username
    return render_template('userHome.html', title=title, username=username)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))