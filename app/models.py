from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import hashlib
from datetime import datetime

# Create database and user model
db = SQLAlchemy()

# Association table (model not necessary because no new data other than foreign keys)
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-viii-followers
# https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html
# https://docs.sqlalchemy.org/en/14/orm/relationship_api.html#sqlalchemy.orm.relationship.params.backref
stalkers = db.Table('stalkers', 
    db.Column('stalker_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('stalking_id', db.Integer, db.ForeignKey('users.id')))

likes = db.Table('likes', 
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key = True),
    db.Column('liked_by_id', db.Integer, db.ForeignKey('users.id'), primary_key = True))

categories_stalklist = db.Table('categories_stalklist',
    db.Column('cat_id', db.Integer, db.ForeignKey('categories.id'), primary_key = True),
    db.Column('stalker_id', db.Integer, db.ForeignKey('users.id'), primary_key = True))

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
    
    # Categories that are being stalked by this user
    stalked_categories = db.relationship(
        'CategoryModel', secondary = categories_stalklist,
        #primaryjoin = (stalkers_category.c.cat_id == 'categories.id'),
        back_populates = 'stalked_by')
    
    # Liked/Saved Posts
    liked_posts = db.relationship(
        'PostModel', secondary = likes,
        back_populates = 'liked_by')

    #saved_posts = db.Column(db.Integer, db.ForeignKey('posts.id'))

    # Hash a password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    # Check if plain password matches the hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Set a new avatar. If none used, set default
    def set_avatar(self, avatars, upload = None):
        if upload:
            self.avatar_url = upload
        else:
            email_hash = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
            self.avatar_url = avatars.gravatar(email_hash, size=300)

    # Start stalking a specified user
    def start_stalking(self, user):
        if not self.is_stalking(user):
            self.stalking.append(user)
    
    # Stop stalking a specified user
    def stop_stalking(self, user):
        if self.is_stalking(user):
            self.stalking.remove(user)
    
    # Returns true if user is following indicated user and false otherwise
    def is_stalking(self, user):
        return self.stalking.filter(stalkers.c.stalking_id == user.id).count() > 0
    
    # Return list of users this user is stalking
    def get_stalking(self):
        return self.stalking.filter(stalkers.c.stalking_id)

    # Return list of users who are stalking this user
    def get_stalkers(self):
        return self.stalkers.filter(stalkers.c.stalker_id)
    
    # Get posts from stalkees, ordering by timestamp
    def stalked_submissions(self):
        return SubmissionModel.query.join(
            stalkers, (stalkers.c.stalking_id == SubmissionModel.user_id)).filter( # All posts that are being stalked
                stalkers.c.stalker_id == self.id).order_by( # Only get posts that are stalked by this user
                    SubmissionModel.timestamp.desc()) # Order by time, with first result being most recent
    
    # Like a post
    def like_post(self, post):
        if not post.is_liked_by(self):
            self.liked_posts.append(post)

    # Unlike a post    
    def unlike_post(self, post):
        if post.is_liked_by(self):
            self.liked_posts.remove(post)
    
    # Start stalking a specified category
    def start_stalking_cat(self, category):
        if not category.is_stalked_by(self):
            self.stalked_categories.append(category)
    
    # Stop stalking a specified category
    def stop_stalking_cat(self, category):
        if category.is_stalked_by(self):
            self.stalked_categories.remove(category)

class PostModel(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(300), default = "")
    desc = db.Column(db.String(40000), default = "")
    timestamp = db.Column(db.DateTime(), index = True, default = datetime.utcnow)
    type = db.Column(db.String(), default = "")

    __mapper_args__ = {
        'polymorphic_identity': 'post',
        'polymorphic_on': type
    }

    # User interaction
    liked_by = db.relationship(
        'UserModel', secondary = likes,
        back_populates = 'liked_posts')
    
    replies = db.relationship(
        'CommentModel', backref = db.backref('parent', remote_side=[id]),
        lazy = 'dynamic')

    # Check if a user has liked this post
    def is_liked_by(self, user):
        return user in self.liked_by
    
    # Add comment to post's replies table
    def add_comment(self, comment):
        self.replies.append(comment)

# TODO: Link to category by category id instead of name
class SubmissionModel(PostModel):
    __tablename__ = 'submission'
    
    id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key = True)
    category = db.Column(db.String(32), default = "default")
    content = db.Column(db.String(), default = "")

    __mapper_args__ = {
        'polymorphic_identity': 'submission'
    }

class CommentModel(PostModel):
    __tablename__ = 'comments'
    
    parent_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    __mapper_args__ = {
        'polymorphic_identity': 'comment'
    }

class CategoryModel(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(32), default = "default")
    desc = db.Column(db.String(1000), default = "")
    icon = db.Column(db.String())
    creation_date = db.Column(db.DateTime(), index = True, default = datetime.utcnow)

    stalked_by = db.relationship(
        'UserModel', secondary = categories_stalklist,
        #primaryjoin = (stalkers_category.c.stalker_id == 'users.id'),
        back_populates = 'stalked_categories')
    
    # Check if user is stalking this category
    def is_stalked_by(self, user):
        return user in self.stalked_by
