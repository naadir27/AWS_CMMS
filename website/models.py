from flask_login import UserMixin
from . import db

class User(UserMixin):
    def __init__(self, id, username, email, password, is_admin):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.is_admin = is_admin

    @staticmethod
    def get_by_id(user_id):
        cursor = db.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            return User(id=user[0], username=user[1], email=user[2], password=user[3], is_admin=user[4])
        return None

    @staticmethod
    def get_by_email(email):
        cursor = db.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE user_email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            return User(id=user[0], username=user[1], email=user[2], password=user[3], is_admin=user[4])
        return None

    def get_id(self):
        return str(self.id)
