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
    categories = db.relationship('CategoryModel', backref = 'user', lazy = 'dynamic')
    posts = db.relationship('PostModel', backref = 'author', lazy = 'dynamic')

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

class PostModel(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category = db.Column(db.String(32), default = "none")
    title = db.Column(db.String(300), default = "")
    content = db.Column(db.String(), default = "")
    desc = db.Column(db.String(40000), default = "")
    timestamp = db.Column(db.DateTime(), index = True, default = datetime.utcnow)

class CategoryModel(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(32), default = "none")
    desc = db.Column(db.String(40000), default = "")
    icon = db.Column(db.String())
    creation_date = db.Column(db.DateTime(), index = True, default = datetime.utcnow)





