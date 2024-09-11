# Import the necessary modules
import mysql.connector 
from mysql.connector import connect, cursor
from dotenv import load_dotenv
import os
from flask import Flask
from flask_bcrypt import Bcrypt

from flask_jwt_extended import JWTManager

# Load environment variables from .env file
load_dotenv()

# Initialize Bcrypt
bcrypt = Bcrypt()
jwt= JWTManager()

# Function to create and configure the Flask application
def create_app():
    # Create an instance of the Flask class for the web application
    app = Flask(__name__)
    
    # Load secret key and database credentials from environment variables
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
    app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
    app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
    app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
    # app.config['FLASK_JWT_SECRET_KEY'] = os.getenv('FLASK_JWT_SECRET_KEY')
    
    # Initialize Bcrypt with the Flask app
    bcrypt.init_app(app)
    
    # Set up JWT manager
    jwt.init_app(app)

    # Create a function to get a new MySQL connection
    def get_db_connection():
        return mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            password=app.config['MYSQL_PASSWORD'],
            user=app.config['MYSQL_USER'],
            database=app.config['MYSQL_DB'],
        )
    
    # print(app.config['MYSQL_USER'], app.config['MYSQL_PASSWORD'], app.config['MYSQL_HOST'],  app.config['MYSQL_DB'])

    # Make the database connection function accessible within app context
    app.get_db_connection = get_db_connection

    # Import and register blueprints for views and authentication routes
    from .forms import auth_forms
    from .views import views

    app.register_blueprint(auth_forms)
    app.register_blueprint(views, url_prefix='/')

    # Return the configured Flask application instance
    return app
