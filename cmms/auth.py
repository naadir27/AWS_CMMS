from mysql.connector import connect, cursor
from flask import Blueprint, Response, render_template, flash, redirect, url_for, request, current_app
from .forms import LoginForm

auth = Blueprint('auth', __name__)

@auth.route("/login", methods=['GET','POST'])
def login():
    active_page = 'home'
    title = "CMMS Login"

    form = LoginForm()
    
    if form.validate_on_submit():  # This checks if the form is submitted and validated
        # Process login logic here, such as verifying user credentials
        email = form.email.data
        password = form.password.data
        
        # Example: Implement your own logic to check email and password
        if email == "test@example.com" and password == "password123":
            flash('Login successful!', 'success')
            return redirect(url_for('home'))  # Redirect to a 'home' route after successful login
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    
    return render_template('login1.html', form=form, title = title, active_page = active_page)

@auth.route('/logout')
# Ensures the user is logged in before logging out
def logout():
    """
    Route to handle user logout.
    The user must be logged in to access this page.
    """
    # Log out the current user and end their session
    flash("User Successfully Logged Out", "success")  # Flash a success message indicating the user has logged out
    return redirect(url_for('auth.login')) 
