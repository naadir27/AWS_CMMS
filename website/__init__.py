from flask import Flask
from flask_mysqldb import MySQL
from os import path
from flask_login import LoginManager

db = MySQL()

def create_app():
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '0011336e0a2a3e8d9406f3bac794d81500cb22a298bcb39d0c73b5606dda0c5e'
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:naadir123@localhost:3306/userdb'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'naadir123'
    app.config['MYSQL_DB'] = 'userdb'
    app.config['MYSQL_HOST'] = 'localhost'
    db.init_app(app)

    # Initialize LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # Route where the login page is located
    login_manager.init_app(app)

    # User loader callback for Flask-Login
    from .models import User  # Import your User model

    @login_manager.user_loader
    def load_user(user_id):
        cursor = db.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            return User(id=user[0], username=user[1], email=user[2])
        return None

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)
    
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app

