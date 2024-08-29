# Import the necessary modules
from flask import Flask  # The core class for initializing a Flask application
from flask_mysqldb import MySQL  # Flask extension for connecting to a MySQL database
from flask_login import LoginManager  # Flask extension for managing user sessions and handling authentication
from flask_bcrypt import Bcrypt  # Flask extension for password hashing

# Initialize the MySQL object, which will be used to interact with the MySQL database
db = MySQL()

# Intialize Bcrypt
bcrypt = Bcrypt()

# Define a function to create and configure the Flask application
def create_app():
    
    # Create an instance of the Flask class for the web application
    app = Flask(__name__)
    
    # Configure the Flask application with various settings, including the secret key and MySQL database credentials
    app.config['SECRET_KEY'] = '0011336e0a2a3e8d9406f3bac794d81500cb22a298bcb39d0c73b5606dda0c5e'  # Secret key for session management and security, should be set to a strong random value
    app.config['MYSQL_USER'] = 'root'  # MySQL database username
    app.config['MYSQL_PASSWORD'] = 'naadir123'  # MySQL database password
    app.config['MYSQL_DB'] = 'cmms_dup'  # Name of the MySQL database to use
    app.config['MYSQL_HOST'] = 'localhost'  # Hostname of the MySQL server
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # Use dictionary-based cursor for MySQL queries, returning results as dictionaries
    
    # Initialize the MySQL extension with the Flask application instance
    db.init_app(app)
    
    # Import blueprints for views and authentication routes
    from .models import User  # Import the User model from your models module
    from .views import views  # Import the views blueprint from the views module
    from .auth import auth  # Import the auth blueprint from the auth module

    # Register the blueprints with the Flask application
    app.register_blueprint(views, url_prefix='/')  # Register the views blueprint with a URL prefix of '/'
    app.register_blueprint(auth, url_prefix='/')  # Register the auth blueprint with a URL prefix of '/'

    # Create an instance of the LoginManager class
    login_manager = LoginManager()

    # Specify the view to redirect users to if they need to log in
    login_manager.login_view = 'auth.login' 

    # Initialize the LoginManager with the Flask app
    login_manager.init_app(app)

    # Define a function to load a user from the database given their user ID
    @login_manager.user_loader
    def load_user(user_id):
        # Use the User model's method to retrieve the user by ID
        return User.get_by_id(user_id)

    # Return the configured Flask application instance
    return app