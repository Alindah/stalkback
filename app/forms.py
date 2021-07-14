from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import validators, ValidationError

class LoginForm(FlaskForm):
    email = StringField("Email ", [validators.Required("Enter your email address."), 
                                validators.Email("Enter a proper email address.")])
    password = PasswordField("Password ", [validators.Required("Enter a password.")])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Log in")

class RegisterForm(FlaskForm):
    email = StringField("Email* ", [validators.Required("Enter your email address."), 
                                validators.Email("Enter a proper email address.")])
    username = StringField("Username* ", [validators.Required("Enter a username.")])
    display_name = StringField("Display Name ")
    password = PasswordField("Password* ", [validators.Required("Enter a password.")])
    password_check = PasswordField("Re-enter password* ", [validators.Required("Retype your password.")])
    submit = SubmitField("Send")

class SettingsForm(FlaskForm):
    display_name = StringField("Display Name ")
    password = PasswordField("Old password ")
    password_new = PasswordField("New password ")
    password_check = PasswordField("Re-enter password ")
    submit = SubmitField("Save")
