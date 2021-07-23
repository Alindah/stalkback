from flask import Flask, jsonify, render_template, request, redirect, flash, Markup, url_for
from flask.helpers import send_from_directory
from flask_login import login_required, current_user, login_user, logout_user
from models import UserModel, PostModel, db, login
from forms import RegisterForm, SettingsForm, LoginForm, DeleteForm, SearchBar, PostForm, DeletePost
from flask_sqlalchemy import SQLAlchemy
#from flask_migrate import Migrate
from sqlalchemy import or_
from flask_avatars import Avatars
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login.init_app(app)
avatars = Avatars(app)
#migrate = Migrate(app, db)

# Default to here if unauthenticated user attempts to access login required pages
login.login_view = '/'

@app.before_first_request
def create_table():
    db.create_all()

# INDEX / LOGIN
@app.route('/', methods = ['GET', 'POST'])
def index():
    form = LoginForm()

    if current_user.is_authenticated:
        return redirect('/dashboard')
    
    if request.method == 'POST':
        email = request.form['email']
        user = UserModel.query.filter_by(email = email).first()

        if user is None:
            flash("Oops, user doesn't exist. Please register first.")
        else:
            if user.check_password(request.form['password']):
                login_user(user, remember='remember' in request.form)
                return redirect('/dashboard')
            
            flash("Password does not match records. Please try again.")

    return render_template('index.html', form = form)

# REGISTRATION
@app.route('/register', methods = ['GET', 'POST'])
def register():
    contains_err = False
    form = RegisterForm()

    if current_user.is_authenticated:
        return redirect('/dashboard')

    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        display_name = request.form['display_name']
        password = request.form['password']
        password_check = request.form['password_check']

        if UserModel.query.filter_by(email = email).first():
            flash("Email already exists")
            contains_err = True
        
        if UserModel.query.filter_by(username = username).first():
            flash("Username is already taken")
            contains_err = True
        
        if password != password_check:
            flash("Passwords do not match")
            contains_err = True
        
        if not (email and username and password):
            flash("Required information is missing")
            contains_err = True

        if contains_err:
            return redirect('/register')
        
        if not display_name:
            display_name = username

        user = UserModel(email = email, username = username, display_name = display_name)
        user.set_password(password)
        user.set_avatar(avatars)
        db.session.add(user)
        db.session.commit()

        flash("Account successfully created! Please log in.")
        return redirect('/')

    return render_template('register.html', form = form)

# ABOUT
@app.route('/about')
def about():
    return render_template('about.html')

# LOGOUT
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

# ACCOUNT DELETION
@app.route('/deactivate')
@login_required
def deactivate():
    db.session.delete(current_user)
    db.session.commit()
    flash("Your account was successfully deleted.")
    return redirect('/logout')

# DASHBOARD
@app.route('/dashboard', methods = ['GET', 'POST'])
@login_required
def dashboard():
    search_bar = SearchBar()
    if request.method == 'POST':
        if search_bar.search.data:
            return search(request.form['search_query'])

    return render_template('dashboard.html', sb = search_bar)

# SEARCH
@app.route('/search', methods = ['GET', 'POST'])
@login_required
def search(sq):
    search_bar = SearchBar()
    results = None

    if sq.isspace() or sq == "":
        flash("Enter a name or username to search")
    else:
        results = UserModel.query.filter(or_(UserModel.display_name.contains(sq), UserModel.username.contains(sq))).all()

        if not results:
            flash("No users found")
    
    return render_template('search.html', sb = search_bar, res = results)

# SETTINGS
@app.route('/settings', methods = ['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    form_delete = DeleteForm()

    if request.method == 'POST':
        if form_delete.del_confirmation.data:
            if current_user.check_password(request.form['password_del']):
                return redirect('/deactivate')

            flash("Incorrect password. Account is not deleted.")
        
        if form.submit.data:
            display_name = request.form['display_name']
            password_new = request.form['password_new']
            password_check = request.form['password_check']

            if display_name != current_user.display_name:
                if display_name == "":
                    flash("Display name must be at least 1 character long.")
                else:
                    current_user.display_name = display_name
                    flash("Display name successfully changed")
            
            if password_new or password_check:
                if not current_user.check_password(request.form['password']):
                    flash("Old password required to change password")
                elif password_new != password_check:
                    flash("New passwords must match")
                else:
                    current_user.set_password(password_new)
                    flash("Password successfully changed")

            db.session.commit()

    return render_template('settings.html', form = form, form_delete = form_delete)

# PROFILE
@app.route('/stalk/<username>', methods = ['GET', 'POST'])
@login_required
def profile(username): 
    user = UserModel.query.filter_by(username = username).first_or_404()
    posts = reversed(user.posts.all())
    form_del = DeletePost()

    if request.method == 'POST':
        # Delete post
        if form_del.del_post.data:
            db.session.delete(PostModel.query.get(request.form['del_id']))
            db.session.commit()
            return redirect(url_for('profile', username = username))

    return render_template('profile.html', user = user, posts = posts, del_form = form_del)

@app.route('/post', methods = ['POST', 'GET'])
@login_required
def post():
    form = PostForm()

    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        content = request.files['content']
        cat = request.form['category']

        post = PostModel(author = current_user, title = title, desc = desc, category = cat)
        db.session.add(post)
        db.session.commit()

        flash("Posted successfully!")

        return redirect('/post')

    return render_template('post.html', form = form)

app.run(host = 'localhost', port = '5000', debug = True)




