# Import necessary modules and classes

# Import UserMixin, a Flask-Login class that provides default implementations for user authentication methods
from flask_login import UserMixin 

from flask_wtf import FlaskForm # Import FlaskForm from Flask-WTF, which provides integration of WTForms with Flask

from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField # Import form fields from WTForms

from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp # Import validators from WTForms

from . import db # Import the db object from the current package, which is used to interact with the database

from . import bcrypt # Import the brcypt from the current package, which is used to hash the password

"""Creating User Class"""  
# Define the User class that extends UserMixin for Flask-Login integration
class User(UserMixin):
    # Initialize the User object with various attributes
    def __init__(self, username, email, password, user_level, is_admin, id=None):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.user_level = user_level
        self.is_admin = is_admin

    """Funtion called to Get the User_ID From Database"""
    @staticmethod
    def get_by_id(user_id):
        # Create a cursor to execute the SQL query
        cursor = db.connection.cursor()
        
        # Execute the query to select the user with the given ID from the users table
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
        
        # Fetch the user data from the database
        user = cursor.fetchone()
        
        # Close the cursor after the operation
        cursor.close()
        
        # If a user is found, create and return a User object using the retrieved data
        if user:
            return User(
                id=user['user_id'],  # Map the user ID from the database
                username=user['user_name'],  # Map the username from the database
                email=user['user_email'],  # Map the email from the database
                password=user['user_password'],  # Map the password from the database (should be hashed)
                user_level=user['user_level'],  # Map the user level from the database
                is_admin=user['is_admin']  # Map the admin status from the database
            )
        
        # If no user is found, return None
        return None

    # Define a method to get the user's ID, which Flask-Login requires
    def get_id(self):
        # Return the user ID as a string
        return str(self.id)
    
    """Funtion called by Login to Get the Email From Database"""
    @staticmethod
    def get_by_email(email):
        cursor = db.connection.cursor() # Create a cursor to execute the SQL query
        cursor.execute('SELECT * FROM users WHERE user_email = %s', (email,)) # Execute the query to select the user with the email from the users table
        user = cursor.fetchone() # Fetch the user data from the database
        cursor.close() # Close the cursor after the operation
        if user:
            return User(id=user['user_id'], username=user['user_name'], email=user['user_email'], password=user['user_password'], user_level=user['user_level'], is_admin=user['is_admin'])
        return None

    # Method to hash the user's password using bcrypt
    """Hash the password using bcrypt."""
    def set_password(self, password):      
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Method to verify the user's password against the stored hashed password
    """Verify the password using bcrypt."""
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    
""" Validating the Signup Form """ 
class RegistrationForm(FlaskForm):
    """
    This class defines the structure and validation rules for the registration form used during user signup.
    """

    # Name field with validation rules
    name = StringField(
        'Name', 
        validators=[
            DataRequired(),  # Ensures the field is not empty
            Length(min=2, max=50)  # Validates the length of the input (between 2 and 50 characters)
        ], 
        render_kw={
            "class": "form-control",  # Sets the CSS class for styling the input field
            "id": "inputName",  # Sets the HTML id attribute for the input field
            "placeholder": "Name",  # Placeholder text displayed inside the input field
            "required": True,  # HTML5 required attribute to enforce client-side validation
            "autofocus": True  # Automatically focuses on this field when the page loads
        }
    )

    # Email field with validation rules
    email = StringField(
        'Email address', 
        validators=[
            DataRequired(),  # Ensures the field is not empty
            Email()  # Validates the format of the input as a valid email address
        ], 
        render_kw={
            "class": "form-control", 
            "id": "inputEmail", 
            "placeholder": "Email address", 
            "required": True  # Enforces client-side validation
        }
    )

    # Password field with complex validation rules
    password = PasswordField(
        'Password', 
        validators=[
            DataRequired(),  # Ensures the field is not empty
            Length(min=8, message='Password must be at least 8 characters long.'),  # Minimum length of 8 characters
            Regexp('(?=.*[a-z])', message="Password must contain at least one lowercase letter."),  # At least one lowercase letter
            Regexp('(?=.*[A-Z])', message="Password must contain at least one uppercase letter."),  # At least one uppercase letter
            Regexp('(?=.*\d)', message="Password must contain at least one digit."),  # At least one digit
            Regexp('(?=.*[@$!%*?&])', message="Password must contain at least one special character.")  # At least one special character
        ], 
        render_kw={
            "class": "form-control", 
            "id": "inputPassword", 
            "placeholder": "Password", 
            "required": True  # Enforces client-side validation
        }
    )
    
    # Confirm password field with validation rules
    confirm_password = PasswordField(
        'Confirm Password', 
        validators=[
            DataRequired(),  # Ensures the field is not empty
            EqualTo('password', message='Passwords must match.')  # Ensures the confirmation matches the password
        ], 
        render_kw={
            "class": "form-control", 
            "id": "confirmPassword", 
            "placeholder": "Confirm Password", 
            "required": True  # Enforces client-side validation
        }
    )
    
    # Select field for user level with predefined choices
    level = SelectField(
        'User Level', 
        choices=[
            ('', 'Select a Level'),  # Placeholder option
            ('MANAGER', 'MANAGER'),  # Manager level
            ('OPERATOR', 'MACHINE OPERATOR'),  # Machine operator level
            ('TECHNICIAN', 'SERVICE TECHNICIAN')  # Service technician level
        ], 
        validators=[DataRequired()],  # Ensures a selection is made
        render_kw={
            "class": "form-control", 
            "id": "inputLevel"  # Sets the HTML id attribute for the select field
        }
    )
    
    # Checkbox to determine if the user is an admin
    is_admin = BooleanField(
        'Register as ADMIN', 
        render_kw={
            "class": "form-check-input"  # Sets the CSS class for styling the checkbox
        }
    )
    
    # Submit button for the form
    submit = SubmitField(
        'Sign Up', 
        render_kw={
            "class": "submit",  # Sets the CSS class for styling the button
            "value": "Sign Up"  # Sets the value attribute for the button
        }
    )


# Define the LoginForm class, which inherits from FlaskForm
class LoginForm(FlaskForm):

    # Define the email field with validation and rendering options
    email = StringField(
        'Email',  # Label for the field
        validators=[DataRequired(), Email()],  # Validators to ensure the field is not empty and contains a valid email address
        render_kw={"placeholder": "Enter your email", "class": "input", "id": "email"}  # Additional attributes for rendering in HTML
    )

    # Define the password field with validation and rendering options
    password = PasswordField(
        'Password',  # Label for the field
        validators=[DataRequired(), Length(min=8)],  # Validators to ensure the field is not empty and has a minimum length of 8 characters
        render_kw={"placeholder": "Enter your password", "class": "input", "id": "pass"}  # Additional attributes for rendering in HTML
    )
    
    # Define the submit button with rendering options
    submit = SubmitField(
        'Login',  # Text displayed on the button
        render_kw={"class": "submit", "value": "Login"}  # Additional attributes for rendering in HTML
    )