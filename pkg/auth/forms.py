from flask_wtf import FlaskForm
from wtforms import (StringField,SubmitField,EmailField,PasswordField,FileField)
from wtforms.validators import Email,DataRequired,Length,EqualTo
from flask_wtf.file import FileField, FileAllowed, FileRequired

class Loginform(FlaskForm):
    username= StringField('username',validators=[DataRequired(message="username is invaild"),Length(min=3,max=15)])
    password=PasswordField('password',validators=[DataRequired(message="password is invaild"),Length(min=3,max=20)])
    login= SubmitField('login')



class Register(FlaskForm):
    firstname=StringField('First Name',validators=[DataRequired()])
    lastname=StringField('Last Name',validators=[DataRequired()])
    email=EmailField('Email Address',validators=[DataRequired(),Email('invaild email address')])
    phone=StringField('Phone Number',validators=[DataRequired(),Length(min=7, message="Phone must be at least 6 characters")])
    image=FileField('Profile Image (Optional)',validators=[ FileAllowed(["jpg", "jpeg", "png", "webp"],message="Images only!")])
    username=StringField('Username',validators=[DataRequired(message='Username Requried'),Length(min=6,message="Username must be at least 6 characters")])
    user_password=PasswordField('Password',validators=[DataRequired(),Length(min=6,max=50)])
    repeat=PasswordField('Confirm Password',validators=[DataRequired(message="Please confirm your password"),EqualTo('user_password',message='passwords must match')])
    submit=SubmitField('Create Account')


    class Meta:
              
            csrf=True
            csrf_time_limit= 2*60*60


    