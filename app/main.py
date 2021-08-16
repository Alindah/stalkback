from flask import Flask, render_template, request, redirect, flash, Markup, url_for
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from werkzeug.utils import secure_filename
from models import UserModel, PostModel, SubmissionModel, CommentModel, CategoryModel, db
from forms import RegisterForm, SettingsForm, LoginForm, DeleteAccount, SearchBar, PostForm, \
                    PostInteraction, EditProfileForm, CategoryDropdown, EmptyForm, AvatarUpload
from sqlalchemy import or_
from flask_avatars import Avatars
from config import Config
import os

app = Flask(__name__)

# Grab config from config.py
app.config.from_object(Config)

# Link flask app with library objects
login = LoginManager()
avatars = Avatars(app)

db.init_app(app)
login.init_app(app)

# Default to here if unauthenticated user attempts to access login required pages
login.login_view = '/'

# Make sure we have tables to work with
@app.before_first_request
def create_table():
    db.create_all()

# Create necessary folders
@app.before_first_request
def create_dir():
    if not os.path.exists("./app/static/" + app.config['AVATAR_SAVE_PATH']):
        os.makedirs("./app/static/" + app.config['AVATAR_SAVE_PATH'])

# Load the indicated user by id
@login.user_loader
def load_user(id):
    return UserModel.query.get(int(id))

# ============= #
# INDEX / LOGIN #
# ============= #
@app.route('/', methods = ['GET', 'POST'])
def index():
    form = LoginForm()

    # Send user to the dashboard if they are already logged in
    if current_user.is_authenticated:
        return redirect('/dashboard')
    
    # Handle POST requests
    if request.method == 'POST':
        email = request.form['email']
        user = UserModel.query.filter_by(email = email).first()

        # If email doesn't exist in the database, flash error message to user
        # Else check if given password matches with the hashed pw in the db
        if user is None:
            flash("Oops, user doesn't exist. Please register first.")
        else:
            if user.check_password(request.form['password']):
                login_user(user, remember='remember' in request.form)
                return redirect('/dashboard')
            
            flash("Password does not match records. Please try again.")

    return render_template('index.html', form = form)

# ============ #
# REGISTRATION #
# ============ #
@app.route('/register', methods = ['GET', 'POST'])
def register():
    contains_err = False
    form = RegisterForm()

    # Send user to the dashboard if they are already logged in
    if current_user.is_authenticated:
        return redirect('/dashboard')

    # Handle POST requests
    if request.method == 'POST':
        # Collect info from form. These info are passed by the HTTP request
        email = request.form['email']
        username = request.form['username']
        display_name = request.form['display_name']
        password = request.form['password']
        password_check = request.form['password_check']

        # User attempted to create account with already existing email
        if UserModel.query.filter_by(email = email).first():
            flash("Email already exists")
            contains_err = True
        
        # Username is already in use
        if UserModel.query.filter_by(username = username).first():
            flash("Username is already taken")
            contains_err = True
        
        # Passwords entered do not match
        if password != password_check:
            flash("Passwords do not match")
            contains_err = True
        
        # User didn't fill in all required information
        # Note: This should not appear with validators in place
        if not (email and username and password):
            flash("Required information is missing")
            contains_err = True

        # Refresh the page and display flashed messages if user made error(s)
        if contains_err:
            return redirect('/register')
        
        # Set username as display name if left blank
        if not display_name:
            display_name = username

        # Create a new user with the existing info
        user = UserModel(email = email, username = username, display_name = display_name)

        # Hash the password and save it with associated user
        user.set_password(password)

        # Set default avatar
        user.set_avatar(avatars)

        # Add user to the db and create the default category for them
        db.session.add(user)
        db.session.add(CategoryModel(user = user))

        # Save to the session to the db
        db.session.commit()

        flash("Account successfully created!")

        return redirect('/')

    return render_template('register.html', form = form)

# ===== #
# ABOUT #
# ===== #
@app.route('/about')
def about():
    return render_template('about.html')

# ====== #
# LOGOUT #
# ====== #
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

# ================ #
# ACCOUNT DELETION #
# ================ #
@app.route('/deactivate')
@login_required
def deactivate():
    db.session.delete(current_user)
    db.session.commit()
    flash("Your account was successfully deleted.")
    return redirect('/logout')

# ========= #
# DASHBOARD #
# ========= #
@app.route('/dashboard', methods = ['GET', 'POST'])
@login_required
def dashboard():
    search_bar = SearchBar()
    post_int = PostInteraction()

    stalked_posts = current_user.stalked_submissions()
    uc_names = [ c.name for c in current_user.stalked_categories ]
    stalked_posts_cat = stalked_posts.filter(SubmissionModel.category.in_(uc_names))

    # Handle POST requests
    if request.method == 'POST':
        # If the search button was pressed, search for the entered query
        if search_bar.search.data:
            return search(request.form['search_query'])

    return render_template('dashboard.html', sb = search_bar, post_int = post_int, stalked_posts = stalked_posts_cat)

# ====== #
# SEARCH #
# ====== #
@app.route('/search', methods = ['GET', 'POST'])
@login_required
def search(sq):
    search_bar = SearchBar()
    results = None

    # If user has entered a blank entry, flash a message
    # Else return users whose username OR display name is similar to the searched term
    if sq.isspace() or sq == "":
        flash("Enter a non-empty name or username in the search bar above")
    else:
        results = UserModel.query.filter(or_(UserModel.display_name.contains(sq), UserModel.username.contains(sq))).all()

        if not results:
            flash("No users found")
    
    return render_template('search.html', sb = search_bar, res = results)

# ============= #
# USER SETTINGS #
# ============= #
@app.route('/settings', methods = ['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    form_delete = DeleteAccount()
    form_avatar = AvatarUpload()

    # Handle POST requests
    if request.method == 'POST':
        # If user confirms their account deletion, check their password and delete their account if match
        if form_delete.del_confirmation.data:
            if current_user.check_password(request.form['password_del']):
                return redirect('/deactivate')

            flash("Incorrect password. Account is not deleted.")
        
        # Upload new avatar
        if form_avatar.upload.data:
            create_dir()
            avatar = request.files['avatar']
            file_ext = os.path.splitext(avatar.filename)[1]

            if file_ext in app.config['AVATAR_UPLOAD_EXTENSIONS']:
                # https://docs.python.org/3/library/io.html#io.IOBase.seek
                file_size = avatar.seek(0, os.SEEK_END)
                
                # Reset position to start of stream
                avatar.seek(os.SEEK_SET)

                # Reject files that are too large
                if file_size > app.config['AVATAR_MAX_SIZE']:
                    flash("Avatar size must be under {0} kb".format(int(app.config['AVATAR_MAX_SIZE'] / 1024)))
                    return redirect('/settings')

                # Save valid avatar
                avatar.filename = "ua{0}{1}".format(str(current_user.id), ".png")
                avatar_path = os.path.join("./app/static/" + app.config['AVATAR_SAVE_PATH'], avatar.filename)
                avatar.save(avatar_path)

                current_user.set_avatar(avatars, avatar_path)                
                db.session.commit()

                flash("New avatar successfully uploaded.")
            else:
                flash("Avatars must have one of the following extensions: " + str(app.config['AVATAR_UPLOAD_EXTENSIONS']))
        
        # Manage changes user wants to make to their account
        if form.submit.data:
            display_name = request.form['display_name']
            password_new = request.form['password_new']
            password_check = request.form['password_check']

            # If display name has changed, flash message if display name is blank
            # Otherwise, set the new display name
            if display_name != current_user.display_name:
                if display_name == "":
                    flash("Display name must be at least 1 character long.")
                else:
                    current_user.display_name = display_name
                    flash("Display name successfully changed")
            
            # If user entered a new password,
            # make sure they have correctly entered their old password
            # and make sure the new passwords match
            if password_new or password_check:
                if not current_user.check_password(request.form['password']):
                    flash("Old password required to change password")
                elif password_new != password_check:
                    flash("New passwords must match")
                else:
                    current_user.set_password(password_new)
                    flash("Password successfully changed")

            db.session.commit()

    return render_template('settings.html', form = form, form_delete = form_delete, form_avatar = form_avatar)

# ======= #
# PROFILE #
# ======= #
# <username> : the username of an existing user
# <category> : an existing category of the indicated user
@app.route('/stalk/<username>', methods = ['GET', 'POST'])
@app.route('/stalk/<username>/<category>', methods = ['GET', 'POST'])
@login_required
def profile(username, category = "default"):
    # Forms
    post_int = PostInteraction()
    button_stalk = EmptyForm()

    # Return user or return 404 if the user does not exist
    user = UserModel.query.filter_by(username = username).first_or_404()

    # Get all posts by this user if category has the default name
    # Otherwise only get categories associated with category in URL
    posts = SubmissionModel.query.filter_by(author = user) \
                if category == "default" else SubmissionModel.query.filter_by(
                    author = user).filter_by(category = category)
    
    # Order the posts by newest
    posts = posts.order_by(SubmissionModel.timestamp.desc()).all()

    # Get the current category its proper info can be retrieved for the profile
    current_cat = user.categories.filter_by(name = category).first_or_404()

    # Create dropdown of categories
    uc_names = [ c.name for c in user.categories.all() ]
    cat_dd = CategoryDropdown(uc_names)

    return render_template('profile.html', category = category, user = user, desc = current_cat.desc, 
                            posts = posts, user_categories = uc_names, cat_dropdown = cat_dd, 
                            post_int = post_int, button_stalk = button_stalk, 
                            stalkers_count = user.get_stalkers().count(), stalking_count = user.get_stalking().count())

# Default category should redirect to the standard profile page
# <username> : the username of an existing user
@app.route('/stalk/<username>/default')
@login_required
def profile_none(username):
    return redirect(url_for('profile', username = username))

# ========= #
# STALKLIST #
# ========= #
# List of all of a users stalkers OR their stalkees depending on <rel>
# <username> : the username of an existing user
# <category> : an existing category of the indicated user
# <rel> : the relationship between the user and the users on the page - 'stalker' or 'stalking'
@app.route('/sl/<username>/<rel>', methods = ['GET', 'POST'])
@app.route('/sl/<username>/<category>/<rel>', methods = ['GET', 'POST'])
@login_required
def stalklist(username, category = "default", rel = "stalking"):
    user = UserModel.query.filter_by(username = username).first_or_404()
    s = None

    # Set s = to either a query of stalkers or of stalkees based off the path
    if rel == "stalkers":
        s = user.get_stalkers()
    elif rel == "stalking":
        s = user.get_stalking()
        
    return render_template('stalklist.html', username = username, category = category,
                            stalkers = s, table_header = rel)

# Default category should redirect to path without "default" in its URL
@app.route('/sl/<username>/default/<rel>')
@login_required
def stalklist_none(username, rel):
    return redirect(url_for('stalklist', username = username, rel = rel))

# ================= #
# POST A SUBMISSION #
# ================= #
@app.route('/post', methods = ['GET', 'POST'])
@login_required
def post():
    # Get all of a user's categories and populate the dropdown with it
    user_categories = current_user.categories.all()
    uc_names = [ c.name for c in user_categories ]
    form = PostForm(uc_names)

    # Get category user is making a post for if user came to page from a profile category
    current_cat = request.args.get('category')
    
    # Set it to blank if user arrived through a different link or default profile new post link
    if current_cat == "default" or not current_cat:
        current_cat = ""

    # Handle POST requests
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        content = request.files['content']
        cat = request.form['category']
        new_cat = request.form['new_cat']

        # If user has entered something in the "create new category" field, set it to whatever they've typed
        if new_cat:
            cat = new_cat

        # Check if new category already exists, and if not, create a new one
        if cat not in uc_names:
            db.session.add(CategoryModel(user = current_user, name = cat))

        # Create the new post with the user filled form info
        post = SubmissionModel(author = current_user, title = title, desc = desc, category = cat)

        db.session.add(post)
        db.session.commit()

        flash("Posted successfully!")

        return redirect('/post')

    return render_template('post.html', form = form, categories = user_categories, current_cat = current_cat)

# ============ #
# EDIT PROFILE #
# ============ #
# <category> : the category a user is editing a profile for
@app.route('/edit/profile/<category>', methods = ['GET', 'POST'])
@login_required
def edit_prof(category):
    # Get category to edit for
    current_cat = current_user.categories.filter_by(name = category).first_or_404()
    
    form = EditProfileForm()
    
    # Fill the form with category's existing data
    form.tagline.data = current_user.tagline
    form.desc.data = current_cat.desc

    # Handle POST requests
    if request.method == 'POST':
        tagline = request.form['tagline']
        desc = request.form['desc']
    
        # Set new data
        current_user.tagline = tagline
        current_cat.desc = desc

        db.session.commit()
        flash("Profile successfully saved")

        return redirect(url_for('edit_prof', category = category))
    
    return render_template('edit_profile.html', category = category, form = form)

# =============== #
# EDIT CATEGORIES #
# =============== #
# Page to manage a user's created categories
@app.route('/edit/categories', methods = ['GET', 'POST'])
@login_required
def categories():
    return render_template('categories.html')

# ===== #
# LIKES #
# ===== #
# Page containing all of a user's liked posts
@app.route('/liked', methods = ['GET', 'POST'])
@login_required
def liked_posts():
    post_int = PostInteraction()
    return render_template('liked_posts.html', post_int = post_int)

# Handle what happens when like button is pressed
@app.route('/handlelike', methods = ['POST'])
@login_required
def handle_like():
    toggle_like(request.form['post_id'])
    return "success"

# Toggle like or unlike depending on if the user has already liked the post or not
def toggle_like(post_id):
    p = PostModel.query.get(int(post_id))

    if not p.is_liked_by(current_user):
        current_user.like_post(p)
    else:
        current_user.unlike_post(p)

    db.session.commit()

# =========== #
# DELETE POST #
# =========== #
@app.route('/handlepostdeletion', methods = ['POST'])
@login_required
def handle_post_del():
    db.session.delete(PostModel.query.get(request.form['post_id']))
    db.session.commit()
    return "success"

# =================== #
# HANDLE POST REPLIES #
# =================== #
@app.route('/reply', methods = ['POST'])
@login_required
def handle_reply():
    reply(request.form['post_id'], request.form['comment'])
    return "success"

# Add a reply to the post being responded to
# post_id : ID of the post being replied to
# comment : The text within the reply
def reply(post_id, comment):
    p = PostModel.query.get(int(post_id))
    c = CommentModel(author = current_user, desc = comment, parent = p)
    p.add_comment(c)
    db.session.commit()

# =============== #
# HANDLE STALKING #
# =============== #
@app.route('/process_stalk', methods = ['POST'])
@login_required
def process_stalk():
    form = list(request.form.items())

    # The first entry [0] contains the key/value for the user's id, with its value being [1]
    user = UserModel.query.get(int(form[0][1]))

    # Start or stop stalking user
    if current_user.is_stalking(user):
        current_user.stop_stalking(user)
    else:
        current_user.start_stalking(user)

    db.session.commit()

    return "success"

# ========================= #
# MANAGE CATEGORIES STALKED #
# ========================= #
@app.route('/process_stalk_categories', methods = ['POST'])
@login_required
def process_stalk_cat():
    form = list(request.form.items())
    user = UserModel.query.get(int(form[0][1]))
    selected_categories = [int(c[0]) for c in form[1 : ]]
    
    # Add checked categories to stalklist
    for cat_id in selected_categories:
        cat = CategoryModel.query.get(cat_id)
        current_user.start_stalking_cat(cat)
    
    # Remove unchecked items from stalklist
    for cat in user.categories:
        if cat.id not in selected_categories:
            current_user.stop_stalking_cat(cat)
    
    db.session.commit()

    return "success"

# ==== #
# TEST #
# ==== #
# Go the /test route and edit this to test whatever you need
@app.route('/test', methods = ['GET', 'POST'])
def test():
    print("Testing!")
    # Use this to delete entries in a table
    #db.session.query(table_name).delete()
    #db.session.commit()

    #p = PostModel.query.get(int(1))
    #c = CommentModel(author = current_user, desc = "I'm a comment", parent = p)
    #CommentModel(author = current_user, desc = "I'm another comment", parent = p)

    #for comment in CommentModel.query.order_by(CommentModel.timestamp.desc()):
        #print('p: {}, {}: {}'.format(comment.parent_id, comment.author.username, comment.desc))
        #p.add_comment(comment)
    
    stalked_posts = current_user.stalked_submissions()
    uc_names = [ c.name for c in current_user.stalked_categories ]
    stalked_posts_cat = stalked_posts.filter(SubmissionModel.category.in_(uc_names))

    for p in stalked_posts_cat:
        print (p.category)

    return render_template('test.html')

app.run(host = 'localhost', port = '5000', debug = True)




