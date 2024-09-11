from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo, Optional

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
            Length(min=8, max=32, message='Password must be at least 8 characters long and maximum 32 letters.'),
            Regexp('(?=.*[a-z])', message="Password must contain at least one lowercase letter."),
            Regexp('(?=.*[A-Z])', message="Password must contain at least one uppercase letter."),
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
        default='',  # Ensures the placeholder option is selected by default
        validators=[DataRequired()],  # Ensures a selection is made
        render_kw={
            "class": "form-control", 
            "id": "inputLevel"  # Sets the HTML id attribute for the select field
        }
    )
       
    # Submit button for the form
    submit = SubmitField(
        'Sign Up', 
        render_kw={
            "class": "submit",  # Sets the CSS class for styling the button
            "value": "Signup"
        }
    )

# Define the LoginForm class
class LoginForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Enter your email", "class": "input", "id": "email"}
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=8)],
        render_kw={"placeholder": "Enter your password", "class": "input", "id": "pass"}
    )
    submit = SubmitField('Login', render_kw={"class": "submit", "value": "Login"} )

class UpdateUserForm(FlaskForm):

    # Name field with validation rules
    name = StringField(
        'Name', 
        validators=[
            DataRequired(),  # Ensures the field is not empty
            Length(min=2, max=32)  # Validates the length of the input (between 2 and 32 characters)
        ], 
        render_kw={
            "class": "form-control",  # Sets the CSS class for styling the input field
            "id": "inputName",  # Sets the HTML id attribute for the input field
            "placeholder": "Name",  # Placeholder text displayed inside the input field
            "required": True,  # HTML5 required attribute to enforce client-side validation
            "autofocus": True  # Automatically focuses on this field when the page loads
        }
    )

    # Password field with complex validation rules
    password = PasswordField(
        'Password',
        validators=[
            Optional(),  # Allow the password to be optional
            Length(min=8, max=32, message='Password must be at least 8 characters long and maximum 32 letters.'),
            Regexp('(?=.*[a-z])', message="Password must contain at least one lowercase letter."),
            Regexp('(?=.*[A-Z])', message="Password must contain at least one uppercase letter."),
            Regexp('(?=.*\d)', message="Password must contain at least one digit."),
            Regexp('(?=.*[@$!%*?&])', message="Password must contain at least one special character.")
        ],
        render_kw={
            "class": "form-control",
            "id": "inputPassword",
            "placeholder": "Password",
            "required": False  # The field is optional
        }
    )

    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            Optional(),
            EqualTo('password', message='Passwords must match.')
        ],
        render_kw={
            "class": "form-control",
            "id": "confirmPassword",
            "placeholder": "Confirm Password",
            "required": False
        }
    )
      
    # Submit button for the form
    submit = SubmitField(
        'Update', 
        render_kw={
            "class": "submit",  # Sets the CSS class for styling the button
            "value": "Update"
        }
    )