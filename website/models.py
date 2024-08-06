import bcrypt
from flask_login import UserMixin
from . import db

class User(UserMixin):
    def __init__(self, id, username, email, password, user_level, is_admin):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.level = user_level
        self.is_admin = is_admin

    @staticmethod
    def get_by_id(user_id):
        cursor = db.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            return User(id=user['user_id'], username=user['user_name'], email=user['user_email'], password=user['user_password'], user_level=user['user_level'], is_admin=user['is_admin'])
        return None

    @staticmethod
    def get_by_email(email):
        cursor = db.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE user_email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            return User(id=user['user_id'], username=user['user_name'], email=user['user_email'], password=user['user_password'], user_level=user['user_level'], is_admin=user['is_admin'])
        return None

    def get_id(self):
        return str(self.id)

    def set_password(self, password):
        """Hash the password using bcrypt."""
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        """Verify the password using bcrypt."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))