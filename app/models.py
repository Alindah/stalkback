from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask import url_for
from config import Config
import hashlib, os
from datetime import datetime

# Create database
db = SQLAlchemy()

# Association tables (model not necessary because no new data other than foreign keys)
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

# ========== #
# USER MODEL #
# ========== #
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
    
    # Categories - one-to-many relationship between a user and their personal categories
    categories = db.relationship('CategoryModel', backref = 'user', lazy = 'dynamic')
    
    # Posts - one-to-many relationship between a user and their posts
    posts = db.relationship('PostModel', backref = 'author', lazy = 'dynamic')

    # Stalkers - many-to-many relationship between two users
    stalking = db.relationship(
        'UserModel', secondary = stalkers,
        primaryjoin = (stalkers.c.stalker_id == id),
        secondaryjoin = (stalkers.c.stalking_id == id),
        backref = db.backref('stalkers', lazy = 'dynamic'), lazy = 'dynamic')
    
    # Categories that are being stalked by this user - many-to-many
    stalked_categories = db.relationship(
        'CategoryModel', secondary = categories_stalklist,
        back_populates = 'stalked_by')
    
    # Liked/Saved Posts - many-to-many
    liked_posts = db.relationship(
        'PostModel', secondary = likes,
        back_populates = 'liked_by')

    # Hash a password
    # password : plain text password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    # Check if plain password matches the hash
    # password : plain text paassword
    # RETURN : boolean
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Set a new avatar. If none used, set default
    # avatars : avatars object
    # upload* : uploaded file or its name/path
    def set_avatar(self, avatars, upload = None):
        if upload:
            self.avatar_url = upload
        else:
            email_hash = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
            self.avatar_url = avatars.gravatar(email_hash, size=300)
    
    # Get the user's avatar if it exists
    # RETURN : the user's avatar image url
    def get_avatar(self):
        url = Config.AVATAR_SAVE_PATH + "/ua" + str(self.id) + ".png"

        if os.path.exists("./app/static/" + url):
            return url_for('static', filename = url)
        
        return self.avatar_url

    # Start stalking a specified user
    # user : user object who will be stalked
    def start_stalking(self, user):
        if not self.is_stalking(user):
            self.stalking.append(user)
    
    # Stop stalking a specified user
    # user : user object who will no longer be stalked
    def stop_stalking(self, user):
        if self.is_stalking(user):
            self.stalking.remove(user)
    
    # Returns true if user is following indicated user and false otherwise
    # user : user who is being stalked (or not)
    # RETURN : boolean
    def is_stalking(self, user):
        return self.stalking.filter(stalkers.c.stalking_id == user.id).count() > 0
    
    # Return list of users this user is stalking
    # RETURN : query of users who this user is stalking
    def get_stalking(self):
        return self.stalking.filter(stalkers.c.stalking_id)

    # Return list of users who are stalking this user
    # RETURN : query of users who are stalking this user
    def get_stalkers(self):
        return self.stalkers.filter(stalkers.c.stalker_id)
    
    # Get posts from stalkees, ordering by timestamp
    # RETURN : query of posts from users who this user is stalking, including categories they are not stalking
    def stalked_submissions(self):
        return SubmissionModel.query.join(
            stalkers, (stalkers.c.stalking_id == SubmissionModel.user_id)).filter( # All posts that are being stalked
                stalkers.c.stalker_id == self.id).order_by( # Only get posts that are stalked by this user
                    SubmissionModel.timestamp.desc()) # Order by time, with first result being most recent
    
    # Like a post
    # post : post object that is being liked
    def like_post(self, post):
        if not post.is_liked_by(self):
            self.liked_posts.append(post)

    # Unlike a post
    # post : post object that is being unliked
    def unlike_post(self, post):
        if post.is_liked_by(self):
            self.liked_posts.remove(post)
    
    # Start stalking a specified category
    # category : category object that will be added to user's stalked
    def start_stalking_cat(self, category):
        if not category.is_stalked_by(self):
            self.stalked_categories.append(category)
    
    # Stop stalking a specified category
    # category : category object that will be removed from user's stalked
    def stop_stalking_cat(self, category):
        if category.is_stalked_by(self):
            self.stalked_categories.remove(category)

# ========== #
# POST MODEL #
# ========== #
class PostModel(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(300), default = "")
    desc = db.Column(db.String(40000), default = "")
    timestamp = db.Column(db.DateTime(), index = True, default = datetime.utcnow)
    type = db.Column(db.String(), default = "")

    # Lets posts be identified by their subclasses under the column "type"
    __mapper_args__ = {
        'polymorphic_identity': 'post',
        'polymorphic_on': type
    }

    # User interaction
    # ================
    # Relationship between users and posts they've liked (many-to-many)
    liked_by = db.relationship(
        'UserModel', secondary = likes,
        back_populates = 'liked_posts')
    
    # Relationship between posts (either submissions or comments) and their replies (comments) (one-to-many)
    replies = db.relationship(
        'CommentModel', backref = db.backref('parent', remote_side=[id]),
        lazy = 'dynamic')

    # Check if a user has liked this post
    # user : user who is being checked for
    # RETURN : boolean
    def is_liked_by(self, user):
        return user in self.liked_by
    
    # Add comment to post's replies table
    def add_comment(self, comment):
        self.replies.append(comment)

# POST > SUBMISSION
# TODO: Link to category by category id instead of name
class SubmissionModel(PostModel):
    __tablename__ = 'submission'
    
    id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key = True)
    category = db.Column(db.String(32), default = "default")
    content = db.Column(db.String(), default = "")

    __mapper_args__ = {
        'polymorphic_identity': 'submission'
    }

# POST > COMMENT
class CommentModel(PostModel):
    __tablename__ = 'comments'
    
    parent_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    __mapper_args__ = {
        'polymorphic_identity': 'comment'
    }

# ============== #
# CATEGORY MODEL #
# ============== #
class CategoryModel(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(32), default = "default")
    desc = db.Column(db.String(1000), default = "")
    icon = db.Column(db.String())
    creation_date = db.Column(db.DateTime(), index = True, default = datetime.utcnow)

    # Relationship between Category and User (many-to-many)
    stalked_by = db.relationship(
        'UserModel', secondary = categories_stalklist,
        back_populates = 'stalked_categories')
    
    # Check if user is stalking this category
    # user : user model who is being checked for stalking
    # RETURN : boolean
    def is_stalked_by(self, user):
        return user in self.stalked_by
