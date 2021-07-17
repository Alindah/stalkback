from flask import Flask, jsonify, render_template, request, redirect, flash, Markup, url_for
from flask.helpers import send_from_directory
from flask_login import login_required, current_user, login_user, logout_user
from models import UserModel, db_user, login
from forms import RegisterForm, SettingsForm, LoginForm, DeleteForm, SearchBar
from sqlalchemy import or_
from flask_avatars import Avatars


app = Flask(__name__)
avatars = Avatars(app)
app.secret_key = "A poorly-kept secret"

# Link flask app and database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set up paths
app.config['AVATARS_SAVE_PATH'] = "./data/user/avatars"

# Change cache age so css changes show
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = -1

db_user.init_app(app)
login.init_app(app)

# Default to here if unauthenticated user attempts to access login required pages
login.login_view = '/'

@app.before_first_request
def create_table():
    db_user.create_all()

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
        db_user.session.add(user)
        db_user.session.commit()

        flash("Account successfully created! Please log in.")
        return redirect('/')

    return render_template('register.html', form = form)

# LOGOUT
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

# ACCOUNT DELETION
@app.route('/deactivate')
@login_required
def deactivate():
    db_user.session.delete(current_user)
    db_user.session.commit()
    flash("Your account was successfully deleted.")
    return redirect('/logout')

# DASHBOARD
@app.route('/dashboard', methods = ['GET', 'POST'])
@login_required
def dashboard():
    search_bar = SearchBar()
    if request.method == 'POST':
        if search_bar.search.data:
            sq = request.form['search_query']
            if sq != "":
                return search(sq)

    return render_template('dashboard.html', sb = search_bar)

# SEARCH
@app.route('/search', methods = ['GET', 'POST'])
@login_required
def search(sq):
    results = UserModel.query.filter(or_(UserModel.display_name.contains(sq), UserModel.username.contains(sq))).all()
    res_list = [[r.username, r.display_name] for r in results]
    return jsonify(res_list)

# SETTINGS
@app.route('/settings', methods = ['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    form_delete = DeleteForm()

    #up_avatar = request.files['uploaded_avatar']

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

            db_user.session.commit()
        
        #if up_avatar.filename != "":
            #filename = avatars.save_avatar(up_avatar)
            #current_user.set_avatar(avatars, send_from_directory(app.config['AVATARS_SAVE_PATH'], filename))
            #db_user.session.commit()
        #    pass

    return render_template('settings.html', form = form, form_delete = form_delete)

# PROFILE
@app.route('/stalk/<username>', methods = ['GET', 'POST'])
@login_required
def profile(username): 
    user = UserModel.query.filter_by(username = username).first_or_404();   
    
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]

    return render_template('profile.html', user = user, posts = posts)

@app.route('/post', methods = ['POST', 'GET'])
def post():
    return render_template('post.html')

# ABOUT
@app.route('/about')
def about():
    return render_template('about.html')

app.run(host = 'localhost', port = '5000', debug = True)




