from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed,FileRequired

from wtforms import StringField,SubmitField,EmailField,PasswordField,TextAreaField
from wtforms.validators import DataRequired,Email,EqualTo,Length



class Photoform(FlaskForm):
    photo=FileField(validators=[FileRequired(message='you must choose an image'),FileAllowed(['jpg','png','webp','gif','jpeg'],message='invaild file type')])
    submit=SubmitField('upload file')


class Resetform(FlaskForm):
         
         current_password=PasswordField('Current password',validators=[DataRequired()])
         new_password=PasswordField('New Password',validators=[DataRequired(),Length(min=6,max=50)])
         confirm_password=PasswordField("Confirm New Password",validators=[DataRequired(),EqualTo('new_password',message='Passwords must match')])
         submit=SubmitField('Proceed')
 