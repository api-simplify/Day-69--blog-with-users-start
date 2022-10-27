from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, URL, EqualTo
from flask_ckeditor import CKEditorField

##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class RegisterForm(FlaskForm):
    fname = StringField("First Name")
    lname = StringField("Last Name")
    email = EmailField("Email Address (will be used as username", validators=[DataRequired()])
    password = PasswordField("Enter Password", validators=[DataRequired(), EqualTo('confirm',
                                                                                   message="Passwords must match")])
    confirm = PasswordField("Confirm Password", validators=[DataRequired()])
    who_is_you = CKEditorField("Who are you...really?")
    submit = SubmitField("Create New User")

class LoginForm(FlaskForm):
    login_email = EmailField("Login using your email address", validators=[DataRequired()])
    login_password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")
    register = SubmitField("Let's sign you up!!")

class PostCommentForm(FlaskForm):
    post_content = CKEditorField("Comment on this post")
    submit = SubmitField("Submit Comment")