from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, Length

class UserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), 
                                                   Length(max=20, message="Username should be less than 20 characters!")])
    password = PasswordField("Password", validators=[InputRequired()])
    email = EmailField("Email address", validators=[InputRequired(), 
                                                    Length(max=50, message="Email address should be less than 50 characters!")])
    first_name = StringField("First Name", validators=[InputRequired(), 
                                                    Length(max=30, message="First name should be less than 30 characters!")])
    last_name = StringField("Last Name", validators=[InputRequired(), 
                                                     Length(max=30, message="Last name should be less than 30 characters!")])
    
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), 
                                                   Length(max=20, message="Username should be less than 20 characters!")])
    password = PasswordField("Password", validators=[InputRequired()])


class FeedbackForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired(), Length(max=100, message="Max length is 100 characters!")])
    content = StringField("Content", validators=[InputRequired()])