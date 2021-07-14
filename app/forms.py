from flask_wtf import Form
from wtforms import TextField, PasswordField, RadioField, TextAreaField, IntegerField, SelectField, SubmitField
from wtforms import validators, ValidationError

class RegisterForm(Form):
    email = TextField("Email* ", [validators.Required("Enter your email address."), 
                                validators.Email("Enter a proper email address.")])
    username = TextField("Username* ", [validators.Required("Enter a username.")])
    display_name = TextField("Display Name ")
    password = PasswordField("Password* ", [validators.Required("Enter a password.")])
    password_check = PasswordField("Re-enter password* ", [validators.Required("Retype your password.")])
    submit = SubmitField("Send")
