import uuid
from flask import Blueprint, Flask, abort, flash, jsonify, redirect, request, render_template, make_response, current_app, session, url_for
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, decode_token, get_jwt, set_access_cookies, set_refresh_cookies, unset_jwt_cookies, jwt_required, get_jwt_identity, verify_jwt_in_request
from datetime import datetime, timedelta, timezone
from . import bcrypt

# Define the blueprint
auth_forms = Blueprint('auth_forms', __name__)

@auth_forms.route('/login', methods= ['GET','POST'])
def login():

    try:
        verify_jwt_in_request()  # This will raise an error if the token is not valid
        return redirect(url_for('auth_forms.dashBoard'))  # Redirect to dashboard if token is valid
    except:
        pass  # Let the user proceed to login if no valid token is found

    if request.method == 'GET':
        active_page = 'login'
        title = "CMMS Login"
        return render_template('login.html', title=title, active_page=active_page)

    if request.method == 'POST':
        data = request.get_json()
        if not data or not 'email' in data or not 'password' in data:
            return jsonify({'message': 'Email and password are required'}), 400

        connect = current_app.get_db_connection()
        cursor = connect.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_email = %s", (data['email'],))
        user = cursor.fetchone()

        if not user or not bcrypt.check_password_hash(user['user_password'], data['password']):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        response = jsonify({'message': 'Login Successful '})

        user_identity = {
            'user_id': user['user_id'],
            'user_name': user['user_name'],
            'user_level': user['user_level']
        }


        # After Authenticating the user, Token Generates
        # Generate tokens with specified expiration time
        access_token = create_access_token(identity=user_identity, expires_delta=timedelta(minutes=15))
        # refresh_token = create_refresh_token(identity=user_identity)


        # Sets the token in the cookies
        set_access_cookies(response, access_token, max_age=60*15)
        # set_refresh_cookies(response, refresh_token)

        
        flash('Login successful! Redirecting...', 'success')
        return response, 200

# Route for refreshing token
# @auth_forms.route('/refresh', methods=['POST'])
# @jwt_required(refresh=True)
# def refresh_token():
#     current_user = get_jwt_identity()
#     new_access_token = create_access_token(identity=current_user, fresh=False)
#     response = jsonify(access_token=new_access_token)
#     set_access_cookies(response, new_access_token)
#     return response

# @auth_forms.after_request
# def refresh_expiring_jwts(response):
#     try:
#         exp_timestamp = get_jwt()["exp"]
#         now = datetime.now(timezone.utc)
#         target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
#         if target_timestamp > exp_timestamp:
#             access_token = create_access_token(identity=get_jwt_identity())
#             set_access_cookies(response, access_token)
#         return response
#     except (RuntimeError, KeyError):
#         # Case where there is not a valid JWT. Just return the original response
#         return response

@auth_forms.route('/dashBoard', methods=['GET'])
@jwt_required()
def dashBoard():
    user = get_jwt_identity()
    return render_template('dashBoard.html', title="Dashboard", user = user)


@auth_forms.route('/signup', methods=['GET', 'POST'])
@jwt_required()
def signup():
    user = get_jwt_identity()
    connect = None
    cursor = None

    if request.method == 'GET':
        active_page = 'signup'
        title = "Sign Up"
        return render_template('sign.html', title=title, active_page=active_page , user= user)

    if request.method == 'POST':
        data = request.get_json()
        user_id = str(uuid.uuid4())
        name = data.get('inputName')
        email = data.get('inputEmail')
        password = data.get('inputPassword')
        c_password = data.get('confirmPassword')
        level = data.get('inputLevel')

        # Check if password is empty
        if not password:
            return jsonify({'message': 'Password cannot be empty'}), 400
        
        if not password == c_password:
            response = jsonify({'message': 'Passwords do not match'})
            return response, 401

        try:
            # Hash the password using bcrypt
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            # Establish a connection to the database and insert the new user's details
            connect = current_app.get_db_connection()

            if connect is None:
                raise Exception('Database connection failed')

            cursor = connect.cursor(dictionary=True)

            # Check if the email already exists in the database
            cursor.execute("SELECT * FROM users WHERE user_email = %s", (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash('Email already registered. Please enter a new email.', 'danger')
                return jsonify({"message": "Email already registered. Please enter a new email"}), 401

            # Insert the form data into the database  
            insert_query = "INSERT INTO users (user_id, user_name, user_email, user_password, user_level) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (user_id, name, email, hashed_password, level))
            connect.commit()  # Commit the transaction to save changes to the database

            flash('User registered successfully! Log out and log in with the new user', 'success')
            return jsonify({"message": "User registered successfully! Log out and log in with the new user"}), 200

        except Exception as e:
            if connect:
                connect.rollback()  # Rollback only if connection exists
            flash('User registration failed! Please try again.', 'danger')
            return jsonify({"message": f"Error: {str(e)}"}), 500

        finally:
            if cursor:
                cursor.close()  # Close the cursor only if it was created
            if connect:
                connect.close()  # Close the database connection only if it was established

    return render_template('sign.html', title="Sign Up", active_page='signup', user=user)


@auth_forms.route('/redirect_user')
@jwt_required() # Custom decorator that verifies JWT in session
def redirect_user():
    return render_template('redirect.html', title="Redirecting...")

@auth_forms.route('/update_user/<string:user_id>', methods=['GET', 'POST'])
@jwt_required()
def update_user(user_id):
    user = get_jwt_identity()
    title = "Edit Profile"

    # Connect to the database
    connect = current_app.get_db_connection()
    cursor = connect.cursor(dictionary=True)

    if request.method == 'GET':
        # Fetch the current user's details from the database
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()

        if user:
            # Pass the user's current name to the template
            name = user['user_name']
        else:
            flash('User not found!', 'danger')
            return redirect(url_for('views.dashBoard'))

    if request.method == 'POST':
        data = request.get_json()
        name = data.get('inputName')
        password = data.get('inputPassword')
        c_password = data.get('confirmPassword')

        if not name:
            return jsonify({'message': 'Name is required'}), 400
        
        if password or c_password:  # Check if either password field is filled
            if not password == c_password:
                return jsonify({'message': 'Passwords do not match'}), 400

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
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()

            # user_level = user_level_result['user_level'] if user_level_result else None

            user_identity = {
                'user_id': user['user_id'],
                'user_name': user['user_name'],
                'user_level': user['user_level']
            }

            response = jsonify({'message': 'Updated successfully'})

            #Creates new token
            new_access_token = create_access_token(identity=user_identity, expires_delta=timedelta(minutes=15))
            
            # Updates the token cookie
            set_access_cookies(response, new_access_token, max_age=60*15)
            
            flash('User Profile Updated and Token Regenerated!', 'success')
            
            return response


        except Exception as e:
            connect.rollback()
            flash(f"An error occurred: {str(e)}", 'danger')
            response = jsonify({'message': 'Error: {str(e)}'})
            return response

    cursor.close()
    connect.close()

    return render_template('update_user.html', user_id=user_id, name=name, title=title, user=user)

# blacklisted_tokens = set()

# def add_to_blacklist(jti):
#     blacklisted_tokens.add(jti)

# def is_token_blacklisted(jti):
#     return jti in blacklisted_tokens

@auth_forms.route('/logout', methods=['POST'])
def logout():
    # jti = get_jwt()['jti']  # Unique identifier for the JWT token
    # add_to_blacklist(jti)   # Blacklist the token
    response = jsonify({'message': 'Logout successful'})
    unset_jwt_cookies(response)
    flash('Logout successful!', 'info')
    return response
