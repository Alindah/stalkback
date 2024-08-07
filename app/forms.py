from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, \
                    SelectField, HiddenField, TextAreaField, validators

# ===== #
# LOGIN #
# ===== #
class LoginForm(FlaskForm):
    email = StringField("Email", validators = [validators.Required("Enter your email address."), 
                                validators.Email("Enter a proper email address.")],
                                description = "Email")
    password = PasswordField("Password", [validators.Required("Enter a password.")], description = "Password")
    remember = BooleanField("Remember Me")
    submit = SubmitField("Log In")

# ============ #
# REGISTRATION #
# ============ #
class RegisterForm(FlaskForm):
    email = StringField("Email*", [validators.Required("Enter your email address."), 
                                validators.Email("Enter a proper email address.")],
                                description = "Email*")
    username = StringField("Username*", [validators.Required("Enter a username.")], description = "Username*")
    display_name = StringField("Display Name", description = "Display Name")
    password = PasswordField("Password*", [validators.Required("Enter a password.")], description = "Password*")
    password_check = PasswordField("Re-enter password*", [validators.Required("Retype your password.")], description = "Re-type password*")
    submit = SubmitField("Submit")

# ================ #
# ACCOUNT SETTINGS #
# ================ #
class SettingsForm(FlaskForm):
    display_name = StringField("Display Name")
    password = PasswordField("Old password")
    password_new = PasswordField("New password")
    password_check = PasswordField("Re-enter password")
    submit = SubmitField("Save")

class DeleteAccount(FlaskForm):
    password_del = PasswordField(description = "Password")
    del_confirmation = SubmitField("Delete Account")

class AvatarUpload(FlaskForm):
    avatar = FileField("Avatar", [validators.DataRequired()])
    upload = SubmitField("Upload")

# ========== #
# SEARCH BAR #
# ========== #
class SearchBar(FlaskForm):
    search_query = StringField(description = "∞ Type here to start stalking...")
    search = SubmitField("Search ∞")

# ============== #
# NEW SUBMISSION #
# ============== #
class PostForm(FlaskForm):
    title = StringField("Title*", validators = [validators.DataRequired("Title required")], description = "Enter a title")
    content = FileField("Content")
    desc = TextAreaField("Description", description = "Enter a description")
    category = SelectField("Category")
    new_cat = StringField(description = "Create new category")
    submit = SubmitField("Post!")

    def __init__(self, user_cat = ["default"], current_cat = "default"):
        super(PostForm, self).__init__()
        self.category.choices = user_cat

# ====================== #
# POST INTERACTION TOOLS #
# ====================== #
class PostInteraction(FlaskForm):
    post_id = HiddenField("Post ID")
    comment = TextAreaField("Comment", description = "Reply to post...")

# ======= #
# PROFILE #
# ======= #
# EDIT PROFILE
class EditProfileForm(FlaskForm):
    tagline = TextAreaField("Tagline", description = "Enter a tagline. Affects all of your categories.")
    desc = TextAreaField("Description", description = "Enter a description. This only affects the current category.")
    submit = SubmitField("Save")

# CATEGORY DROPDOWN
class CategoryDropdown(FlaskForm):
    category = SelectField("Category")

    def __init__(self, user_cat = [], current_cat = "default"):
        super(CategoryDropdown, self).__init__()
        self.category.choices = ['Select a category...'] + user_cat

# ======= #
# GENERIC #
# ======= #
# Form that trigger a POST request with no data attached
class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")
