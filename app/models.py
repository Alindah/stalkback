from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
import hashlib
from datetime import datetime

# Create database and user model
db = SQLAlchemy()

class UserModel(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(254), unique = True)
    username = db.Column(db.String(30), unique = True)
    display_name = db.Column(db.String(32))
    avatar_url = db.Column(db.String())
    password_hash = db.Column(db.String())
    join_date = db.Column(db.DateTime, default = datetime.utcnow)
    
    # Optional info
    birthday = db.Column(db.DateTime)
    sex = db.Column(db.String(16), default="unset")

    # Profile
    tagline = db.Column(db.String(128), default="")
    last_seen = db.Column(db.DateTime, default = datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_avatar(self, avatars, upload = None):
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

class PostModel():
    __tablename__ = 'posts'
"""
    id = db.Column(db.Integer, primary_key = True)
    author = db.Column(db.String(32))
    title = db.Column(db.String())
    content = db.user.Column()
    desc = db.Column(db.String())"""

class CategoryModel():
    __tablename__ = 'categories'





