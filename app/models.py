from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import hashlib
from datetime import datetime

# Create database and user model
db = SQLAlchemy()

# Association table (model not necessary because no new data other than foreign keys)
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-viii-followers
stalkers = db.Table('stalkers', 
    db.Column('stalker_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('stalking_id', db.Integer, db.ForeignKey('users.id')))

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

    # Stalkers
    stalking = db.relationship(
        'UserModel', secondary = stalkers,
        primaryjoin = (stalkers.c.stalker_id == id),
        secondaryjoin = (stalkers.c.stalking_id == id),
        backref = db.backref('stalkers', lazy = 'dynamic'), lazy = 'dynamic')

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

    def start_stalking(self, user):
        if not self.is_stalking(user):
            self.stalking.append(user)
    
    def stop_stalking(self, user):
        if self.is_stalking(user):
            self.stalking.remove(user)
    
    # Returns true if user is following indicated user and false otherwise
    def is_stalking(self, user):
        return self.stalking.filter(stalkers.c.stalking_id == user.id).count() > 0
    
    # Return list of users this user is stalking
    def get_stalking(self):
        return self.stalking.filter(stalkers.c.stalking_id)
    
    # Get posts from stalkees, ordering by timestamp
    def stalked_posts(self):
        return PostModel.query.join(
            stalkers, (stalkers.c.stalking_id == PostModel.user_id)).filter( # All posts that are being stalked
                stalkers.c.stalker_id == self.id).order_by( # Only get posts that are stalked by this user
                    PostModel.timestamp.desc()) # Order by time, with first result being most recent


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
    desc = db.Column(db.String(1000), default = "")
    icon = db.Column(db.String())
    creation_date = db.Column(db.DateTime(), index = True, default = datetime.utcnow)





