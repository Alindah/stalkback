from flask import Flask, render_template, request, redirect, flash, Markup, url_for
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from models import UserModel, PostModel, CategoryModel, db
from forms import RegisterForm, SettingsForm, LoginForm, DeleteAccount, SearchBar, PostForm, DeletePost, EditProfileForm, CategoryDropdown, EmptyForm
from sqlalchemy import or_
from flask_avatars import Avatars
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Link Flask_Login and database
login = LoginManager()

db.init_app(app)
login.init_app(app)
avatars = Avatars(app)

# Default to here if unauthenticated user attempts to access login required pages
login.login_view = '/'

@app.before_first_request
def create_table():
    db.create_all()

@login.user_loader
def load_user(id):
    return UserModel.query.get(int(id))

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
        db.session.add(CategoryModel(user = user, name = "none"))
        db.session.commit()

        flash("Account successfully created!")
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
    form_delete = DeleteAccount()

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
@app.route('/stalk/<username>/<category>', methods = ['GET', 'POST'])
@login_required
def profile(username, category = "none"):
    form_del = DeletePost()
    button_stalk = EmptyForm()
    user = UserModel.query.filter_by(username = username).first_or_404()
    posts = user.posts.all() if category == "none" else user.posts.filter_by(category = category).all()
    current_cat = user.categories.filter_by(name = category).first_or_404()
    uc_names = [ c.name for c in user.categories.all() ]
    cat_dd = CategoryDropdown(uc_names)

    if request.method == 'POST':
        # Start/stop stalking
        if button_stalk.submit.data:
            if current_user.is_stalking(user):
                current_user.stop_stalking(user)
            else:
                current_user.start_stalking(user)
            
            db.session.commit()
            
            return redirect(url_for('profile', username = username))

        # Delete post
        if form_del.del_post.data:
            db.session.delete(PostModel.query.get(request.form['del_id']))
            db.session.commit()
            return redirect(url_for('profile', username = username))

    return render_template('profile.html', category = category, user = user, desc = current_cat.desc, 
                            posts = reversed(posts), user_categories = uc_names, cat_dropdown = cat_dd, 
                            del_form = form_del, button_stalk = button_stalk)

@app.route('/stalk/<username>/none')
@login_required
def profile_none(username):
    return redirect(url_for('profile', username = username))

@app.route('/post', methods = ['POST', 'GET'])
@login_required
def post():
    user_categories = current_user.categories.all()
    uc_names = [ c.name for c in user_categories ]
    form = PostForm(uc_names)

    current_cat = request.args.get('category')
    
    if current_cat == "none" or not current_cat:
        current_cat = ""

    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        content = request.files['content']
        cat = request.form['category']
        new_cat = request.form['new_cat']

        if new_cat:
            cat = new_cat

        if cat not in uc_names:
            db.session.add(CategoryModel(user = current_user, name = cat))

        post = PostModel(author = current_user, title = title, desc = desc, category = cat)
        db.session.add(post)
        db.session.commit()

        flash("Posted successfully!")

        return redirect('/post')

    return render_template('post.html', form = form, categories = user_categories, current_cat = current_cat)

# EDIT PROFILE
@app.route('/edit/profile/<category>', methods = ['POST', 'GET'])
@login_required
def edit_prof(category):
    current_cat = current_user.categories.filter_by(name = category).first_or_404()
    form = EditProfileForm()
    form.tagline.data = current_user.tagline
    form.desc.data = current_cat.desc

    if request.method == 'POST':
        tagline = request.form['tagline']
        desc = request.form['desc']
    
        current_user.tagline = tagline
        current_cat.desc = desc

        db.session.commit()
        flash("Profile successfully saved")

        return redirect(url_for('edit_prof', category = category))
    
    return render_template('edit_profile.html', category = category, form = form)

app.run(host = 'localhost', port = '5000', debug = True)




