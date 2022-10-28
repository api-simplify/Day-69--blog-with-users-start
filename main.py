# import time

import flask_login
import os
from flask import Flask, render_template, redirect, url_for, flash, jsonify, session
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm, PostCommentForm
from flask_gravatar import Gravatar
from decorators import admin_only
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


login_manager = LoginManager()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# app.secret_key = ':dFU3ivDT1tA)mGG1a'
login_manager.init_app(app)
login_manager.login_message = "You must login to view this page."
# login_manager.login_view = ""
# print(vars(db.session))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# CONFIGURE TABLES


class User(UserMixin, db.Model, Base):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    posts = relationship('BlogPost')
    comments = relationship('Comments')
    fname = db.Column(db.String(100), nullable=True)
    lname = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(200), nullable=False)
    who_is_you = db.Column(db.Text, nullable=True)
    reg_date = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    is_admin = db.Column(db.Integer(), nullable=True)


class BlogPost(db.Model, Base):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    comments = relationship("Comments")
    author_id = db.Column(db.Integer, ForeignKey('user.id'))
    author = relationship("User", back_populates="posts")  # db.Column(db.String(250), nullable=False)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


class Comments(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, ForeignKey("user.id"))
    author = relationship("User", back_populates="comments")
    post_id = db.Column(db.Integer, ForeignKey("blog_posts.id"))
    post = relationship("BlogPost", back_populates="comments")
    comment = db.Column(db.Text, nullable=False)


# db.create_all()
# def admin_only(func):
#     def wrapper():
#         if current_user.is_admin:
#             func
#         else:
#             flash("You do not have access to do this")
#             return redirect(url_for("get_all_posts"))
#     return wrapper


@app.route('/')
def get_all_posts():
    # flask_login.confirm_login()
    # TODO need to figure out how to log out when browser "TAB" is closed - not just browser
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(
            fname=form.fname.data,
            lname=form.fname.data,
            email=form.email.data,
            who_is_you=form.who_is_you.data,
            reg_date=date.today().strftime("%B %d, %Y"),
            password=generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        )
        if db.session.query(User).filter_by(email=new_user.email).first():
            flash("That email already exists. Try logging in instead.")
            print("Email already exists.")
            return redirect(url_for("login"))
        try:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('get_all_posts'))
        except:
            print("Emotional Damage!")
            return jsonify(f"could not create new user {new_user.email}")
        flash("Now let's log in!")
        # return redirect(url_for('login'))
    return render_template("register.html", form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    ##TODO remove requirement for content in form when user selects to go to registration page
    if form.validate_on_submit() and form.register.data:
        return redirect(url_for("register"))
    if form.validate_on_submit():
        # if form.register.data:
        #     return redirect(url_for("register"))
        login_email = form.login_email.data
        login_password = form.login_password.data
        user = db.session.query(User).filter_by(email=login_email).first()
        if not user:
            ##TODO remove detail about failure - no hint as to why they failed to authenticate
            flash("That email does not exist. Please try again or sign up if you are not a member.")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, login_password):
            flash("Invalid password. Please try again or sign up if you are not a member.")
            return redirect(url_for("login"))
        else:
            login_user(user)
            return redirect(url_for("get_all_posts"))
    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=['POST', 'GET'])
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    form = PostCommentForm()
    comments = Comments.query.filter_by(post_id=requested_post.id)
    if form.validate_on_submit():
        if current_user.is_authenticated:
            new_comment = Comments(
                author_id = current_user.id,
                post_id = requested_post.id,
                comment = form.post_content.data
            )
        else:
            new_comment = Comments(
                author_id="",
                post_id=requested_post.id,
                comment=form.post_content.data
            )
        db.session.add(new_comment)
        db.session.commit()
    return render_template("post.html", post=requested_post, form=form, comments=comments)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


##Todo - need to remove admin button for non-admin users and check the "user.is_admin" credential
@app.route("/admin")
def admin_page():
    return render_template("admin.html")


@app.route("/new-post", methods=['POST', 'GET'])
# @login_required
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            author_id=current_user.id,
            date=date.today().strftime("%B, %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>")
@admin_only
# @login_required
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form)


@app.route("/delete/<int:post_id>")
# @login_required
@admin_only
def delete_post(post_id):
    if not current_user.is_admin:
        return redirect(url_for("login"))
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


# @app.route("/comment/<int:post_id>")
# @login_required
# def comment_post(post_id):
#     form = PostCommentForm()
#     # if not current_user.is_active:
#     #     redirect(url_for("login"))
#     if form.validate_on_submit():
#         Comments.comment = form.post_content.data()
#         Comments.post = form.post_id.data()
#         db.session.commit()
#     return redirect(url_for("login"))




if __name__ == "__main__":
    app.run(port=5000, debug=True)
