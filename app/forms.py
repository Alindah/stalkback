from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators
from wtforms.validators import Length

class LoginForm(FlaskForm):
    email = StringField("Email", validators = [validators.Required("Enter your email address."), 
                                validators.Email("Enter a proper email address.")],
                                description = "Email")
    password = PasswordField("Password", [validators.Required("Enter a password.")], description = "Password")
    remember = BooleanField("Remember Me")
    submit = SubmitField("Log In")

class RegisterForm(FlaskForm):
    email = StringField("Email*", [validators.Required("Enter your email address."), 
                                validators.Email("Enter a proper email address.")],
                                description = "Email*")
    username = StringField("Username*", [validators.Required("Enter a username.")], description = "Username*")
    display_name = StringField("Display Name", description = "Display Name")
    password = PasswordField("Password*", [validators.Required("Enter a password.")], description = "Password*")
    password_check = PasswordField("Re-enter password*", [validators.Required("Retype your password.")], description = "Re-type password*")
    submit = SubmitField("Submit")

class SettingsForm(FlaskForm):
    display_name = StringField("Display Name")
    password = PasswordField("Old password")
    password_new = PasswordField("New password")
    password_check = PasswordField("Re-enter password")
    submit = SubmitField("Save")

class DeleteForm(FlaskForm):
    password_del = PasswordField(description = "Password")
    del_confirmation = SubmitField("Delete Account")

class SearchBar(FlaskForm):
    search_query = StringField(description = "∞ Start stalking...")
    search = SubmitField("oo")
