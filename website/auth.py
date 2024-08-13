# Import wraps from functools to create decorators for functions
from functools import wraps

# Import various functions and classes from Flask
from flask import Blueprint, render_template, request, flash, redirect, url_for, session

# Import Flask-Login components for managing user sessions
from flask_login import login_user, login_required, logout_user, current_user, LoginManager, UserMixin

# Import the database instance from the current package (defined in __init__.py)
from . import db

# Import custom models and forms defined in the current package
from .models import User, LoginForm, RegistrationForm


# Create a blueprint named 'auth' for authentication-related routes
auth = Blueprint('auth', __name__)

# Define a decorator to enforce admin access on certain routes
def admin_required(f):
    @wraps(f)  # Preserve the original function's metadata
    def decorated_function(*args, **kwargs):
        # Check if the current user is authenticated (logged in)
        if not current_user.is_authenticated:
            # If the user is not authenticated, show an error message
            flash('Please log in to access this page.', 'danger')
            # Redirect the user to the login page
            return redirect(url_for('auth.login'))
        
        # Check if the current user has admin privileges
        if not getattr(current_user, 'is_admin', False):
            # If the user is not an admin, show an error message
            flash('You are not authorized to access this page!', 'danger')
            # Redirect the user to the home page or another suitable page
            return redirect(url_for('/'))  # Adjust the redirect URL as needed
        
        # If the user is authenticated and an admin, proceed with the original function
        return f(*args, **kwargs)
    
    # Return the decorated function
    return decorated_function


# Define a route for the login page with both GET and POST methods allowed
@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Set the active page and title for the template (used in the frontend)
    active_page = 'login'
    title = "Login"
    
    # Create an instance of the LoginForm
    form = LoginForm()
    
    # Check if the form was submitted and passes all validation checks
    if form.validate_on_submit():
        # Extract email and password from the form data
        user_email = form.email.data
        user_password = form.password.data
        
        # Attempt to retrieve the user from the database using the provided email
        user = User.get_by_email(user_email)
        
        # Check if the user exists and if the provided password is correct
        if user and user.check_password(user_password):
            # If authentication is successful, flash a success message
            flash('Login successful! Redirecting...', 'success')
            
            # Log the user in and start a session using Flask-Login's login_user function
            login_user(user)
            
            # Redirect the user to their home page (or other appropriate route)
            return redirect(url_for('auth.redirect_user_home'))
        else:
            # If authentication fails, flash an error message
            flash('Invalid credentials!', 'danger')
            
            # Redirect back to the login page to try again
            return redirect(url_for('auth.login'))
    else:
        # If the form was not submitted or didn't pass validation, render the login template
        return render_template('login.html', form=form, title=title, active_page=active_page)



# Define a route for the signup page with both GET and POST methods allowed
@auth.route('/signup', methods=['GET', 'POST'])
@admin_required  # Ensure that only admins can access the signup route
def signup():
    
    # Handle GET requests to display the signup form
    if request.method == 'GET':
        active_page = 'signup'
        title = "Sign Up"
        form = RegistrationForm()  # Create an instance of the RegistrationForm
        
        # Render the signup page with the form
        return render_template('sign.html', title=title, active_page=active_page, form=form)
    
    # Create a new instance of the RegistrationForm to handle POST requests
    form = RegistrationForm()

    # Check if the form was submitted and passes all validation checks
    if form.validate_on_submit():
        # Extract form data for the new user
        name = form.name.data
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        level = form.level.data
        is_admin = 1 if form.is_admin.data else 0  # Determine if the new user should be an admin

        # Create a new User instance with the form data (password will be hashed separately)
        new_user = User(id=id, username=name, email=email, password='', user_level=level, is_admin=is_admin)
        
        # Hash the password using bcrypt and set it for the new user
        new_user.set_password(confirm_password)

        # Establish a connection to the database and insert the new user's details
        cursor = db.connection.cursor()
        insert_query = "INSERT INTO users (user_name, user_email, user_password, user_level, is_admin) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (new_user.username, new_user.email, new_user.password, new_user.user_level, new_user.is_admin))
        db.connection.commit()  # Commit the transaction to save changes to the database
        cursor.close()  # Close the database cursor

        # Display a success message indicating the user was registered successfully
        flash('User registered successfully! Log Out and Log in with the New User', 'success')
        
        # Redirect to the dashboard or another appropriate page
        return redirect(url_for('auth.dashBoard'))
    else:
        # If the form fails validation or registration fails, display an error message
        flash('User registration Failed!', 'danger')
        
        # Redirect back to the signup page to allow the user to try again
        return redirect(url_for('auth.signup'))


@auth.route('/redirect_user_home')
@login_required
def redirect_user_home():
    """
    Route to handle redirection after a user logs in.
    Ensures that the user is authenticated before allowing access to this page.
    """
    return render_template('redirect_user_home.html')  # Render the template for redirecting users after login

# Route for the user dashboard after login
@auth.route('/dashBoard', methods=['GET'])
@login_required  # Ensures the user is logged in before accessing the dashboard
def dashBoard():
    """
    Route to display the user's dashboard.
    The user must be logged in to access this page.
    """
    title = "User Home"  # Set the title for the dashboard page
    username = current_user.username  # Get the username of the current logged-in user
    return render_template('dashBoard.html', title=title, username=username)  # Render the dashboard template with the title and username

@auth.route('/logout')
@login_required  # Ensures the user is logged in before logging out
def logout():
    """
    Route to handle user logout.
    The user must be logged in to access this page.
    """
    logout_user()  # Log out the current user and end their session
    flash("User Successfully Logged Out", "success")  # Flash a success message indicating the user has logged out
    return redirect(url_for('auth.login'))  # Redirect the user to the login page after logging out
