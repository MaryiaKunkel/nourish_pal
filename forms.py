from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, URL

class UserAddForm(FlaskForm):

    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])

class LoginForm(FlaskForm):

    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class EditProfileForm(FlaskForm):
    '''Form for editting profile'''
    first_name=StringField('First name', validators=[DataRequired()])
    last_name=StringField('Last name', validators=[DataRequired()])
    email=StringField('E-mail', validators=[Email()])
    password = PasswordField('Password', validators=[Length(min=6)])