from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager

# Create database and user model
db_user = SQLAlchemy()

class UserModel(UserMixin, db_user.Model):
    __tablename__ = 'users'
    
    id = db_user.Column(db_user.Integer, primary_key = True)
    email = db_user.Column(db_user.String(254), unique = True)
    username = db_user.Column(db_user.String(30), unique = True)
    display_name = db_user.Column(db_user.String(32))
    password_hash = db_user.Column(db_user.String())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self):
        pass

# Link Flask_Login and database
login = LoginManager()

@login.user_loader
def load_user(id):
    return UserModel.query.get(int(id))




class CategoryModel():
    __tablename__ = 'categories'





