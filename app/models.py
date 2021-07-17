from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
import hashlib

# Create database and user model
db_user = SQLAlchemy()

class UserModel(UserMixin, db_user.Model):
    __tablename__ = 'users'
    
    id = db_user.Column(db_user.Integer, primary_key = True)
    email = db_user.Column(db_user.String(254), unique = True)
    username = db_user.Column(db_user.String(30), unique = True)
    display_name = db_user.Column(db_user.String(32))
    avatar_url = db_user.Column(db_user.String())
    password_hash = db_user.Column(db_user.String())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_avatar(self, avatars, upload):
        if upload:
            self.avatar_url = upload
        else:
            email_hash = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
            self.avatar_url = avatars.gravatar(email_hash, size=300)

# Link Flask_Login and database
login = LoginManager()

@login.user_loader
def load_user(id):
    return UserModel.query.get(int(id))

class CategoryModel():
    __tablename__ = 'categories'





