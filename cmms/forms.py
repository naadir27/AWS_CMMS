from flask import Blueprint, render_template, request, flash, redirect, session, url_for, current_app,jsonify
from .models import RegistrationForm, LoginForm, UpdateUserForm
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity, jwt_required
from functools import wraps
import uuid
from . import bcrypt

# Define the blueprint
auth_forms = Blueprint('auth_forms', __name__)

def session_jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = session.get('jwt_token')
        if not token:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('auth_forms.login'))
        try:
            decoded_token = decode_token(token)
            session['current_user'] = decoded_token['sub']['id']
        except Exception as e:
            flash('Invalid or expired token. Please log in again.', 'danger')
            session.pop('jwt_token', None)
            return redirect(url_for('auth_forms.login'))
        return fn(*args, **kwargs)
    return wrapper

# Define a route for the Register page with both GET and POST methods allowed
@auth_forms.route('/register', methods=['GET', 'POST'])
@session_jwt_required
def register():
    if request.method == 'GET':
        active_page = 'register'
        title = "Register User"
        form = RegistrationForm()  # Create an instance of the RegistrationForm
        return render_template('sign.html', title=title, active_page=active_page, form=form)
    
    form = RegistrationForm()

    if form.validate_on_submit():
        user_id = str(uuid.uuid4())
        name = form.name.data
        email = form.email.data
        password = form.password.data
        level = form.level.data

        try:
            # Hash the password using bcrypt
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            # Establish a connection to the database and insert the new user's details
            connect = current_app.get_db_connection()
            cursor = connect.cursor(dictionary=True)

            # Check if the email already exists in the database
            cursor.execute("SELECT * FROM users WHERE user_email = %s", (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash('Email already registered. Please log in.', 'danger')
                return redirect(url_for('auth_forms.register'))

            # Insert the form data into the database  
            insert_query = "INSERT INTO users (user_id, user_name, user_email, user_password, user_level) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (user_id, name, email, hashed_password, level))    
            connect.commit()  # Commit the transaction to save changes to the database
            
            flash('User registered successfully! Log out and log in with the new user', 'success')
            return redirect(url_for('auth_forms.dashBoard'))

        except Exception as e:
            connect.rollback()  # Rollback any changes if an error occurs
            flash('User registration failed! Please try again.', 'danger')
            print(f"Error: {e}")  # Log the error for debugging purposes
        
        finally:
            cursor.close()  # Close the cursor
            connect.close()  # Close the database connection

    # If the form fails validation or registration fails, re-render the register form with error messages
    return render_template('sign.html', title=title, active_page=active_page, form=form)

# Define a route for the login form
@auth_forms.route('/login', methods=['GET', 'POST'])
def login():

    active_page = 'login'
    title = "CMMS Login"

    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        # Get the database connection
        connect = current_app.get_db_connection()
        cursor = connect.cursor(dictionary=True)

        try:
            
            cursor.execute("SELECT * FROM users WHERE user_email = %s", (email,))
            user = cursor.fetchone()

            # Verify the hashed password using Bcrypt
            if user and bcrypt.check_password_hash(user['user_password'], password):
                access_token = create_access_token(identity={
                    'id': user['user_id'],
                    'name': user['user_name'],
                    'level': user['user_level']
                })

                flash(f'Login successful! Token: {access_token}', 'info')
                session['jwt_token'] = access_token
                
                # Decode the JWT token to extract user_name, user_level and user_id
                decoded_token = decode_token(access_token)
                
                # Extract user details from the decoded token
                user_name = decoded_token['sub']['name']  
                user_level = decoded_token['sub']['level']
                user_id = decoded_token['sub']['id']

                # Stores the user details in the session
                session['user_name'] = user_name  
                session['user_level'] = user_level
                session['user_id'] = user_id

                # return jsonify(access_token=access_token)
                # flash(f'Login successful! Redirecting... {user_name}', 'success')
                flash('Login successful! Redirecting...', 'success')
                return redirect(url_for('auth_forms.redirect_user'))
            else:
                flash('Invalid credentials. Please try again.', 'danger')

        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'danger')

        finally:
            # Close the connection
            cursor.close()
            connect.close()
        
        return redirect(url_for('auth_forms.login'))

    return render_template('login.html', form=form, title=title, active_page=active_page)

@auth_forms.route('/redirect_user')
@session_jwt_required # Custom decorator that verifies JWT in session
def redirect_user():
    return render_template('redirect.html')

@auth_forms.route('/dashBoard')
@session_jwt_required  
def dashBoard():
    title="Dashboard"
    user_name = session.get('user_name')
    user_level = session.get('user_level')
    user_id = session.get('user_id')
    return render_template('dashboard.html', title=title, user_name=user_name, user_level=user_level, user_id=user_id)

@auth_forms.route('/logout', methods=['GET'])
def logout():
    """
    Route to handle user logout.
    The user must be logged in to access this page.
    """
    # session.pop('jwt_token', None)
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth_forms.login'))

@auth_forms.route('/update_user/<string:user_id>', methods=['GET', 'POST'])
@session_jwt_required
def update_user(user_id):
    title = "Edit Profile"
    form = UpdateUserForm()

    # Connect to the database
    connect = current_app.get_db_connection()
    cursor = connect.cursor(dictionary=True)

    if request.method == 'GET':
        # Fetch the current user's details from the database
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()

        if user:
            # Pre-fill the form with current user details
            form.name.data = user['user_name']
        else:
            flash('User not found!', 'danger')
            return redirect(url_for('views.dashBoard'))

    if form.validate_on_submit():
        name = form.name.data
        password = form.password.data

        try:
            # Update user profile in the database
            if password:
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                update_query = """
                    UPDATE users
                    SET user_name = %s, user_password = %s
                    WHERE user_id = %s;
                """
                cursor.execute(update_query, (name, hashed_password, user_id))
            else:
                update_query = """
                    UPDATE users
                    SET user_name = %s
                    WHERE user_id = %s;
                """
                cursor.execute(update_query, (name, user_id))

            connect.commit()

        
            # Fetch user_level after update
            cursor.execute("SELECT user_level, user_email FROM users WHERE user_id = %s", (user_id,))
            user_level_result = cursor.fetchone()
            user_level = user_level_result['user_level'] if user_level_result else None

            # Regenerate the JWT token with updated user details
            updated_user = {
                "id": user_id,
                "name": name,
                "level": user_level
            }
            new_token = create_access_token(identity=updated_user)

            # Store the updated token in session
            session['jwt_token'] = new_token
            flash(f'Login successful! Token: {new_token}', 'info')
            
            # Decode the JWT token to extract user_name, user_level and user_id
            decoded_token = decode_token(new_token)
            
            # Extract user details from the decoded token
            user_name = decoded_token['sub']['name']  
            user_level = decoded_token['sub']['level']
            user_id = decoded_token['sub']['id']

            # Stores the user details in the session
            session['user_name'] = user_name  
            session['user_level'] = user_level
            session['user_id'] = user_id

            flash('User Profile Updated and Token Regenerated!', 'success')
            return redirect(url_for('auth_forms.dashBoard'))

        except Exception as e:
            connect.rollback()
            flash(f"An error occurred: {str(e)}", 'danger')

    cursor.close()
    connect.close()

    return render_template('update_user.html', form=form, user_id=user_id, title=title)

@auth_forms.route('/userHome', methods=['GET'])
@jwt_required()
def userHome():
    current_user_id = get_jwt_identity()
    return jsonify(username=current_user_id), 200

@auth_forms.route('/forget')
def forget():

    title = "Forget Password"  # Set the title for the dashboard page
    
    return render_template('forgetpw.html', title=title)