# -*- coding: utf-8 -*-
from enum import Enum
from flask import Flask, render_template, request, flash, redirect, url_for, session
from datetime import timedelta
from markupsafe import Markup
from flask_wtf import FlaskForm, CSRFProtect
from wtforms.validators import DataRequired, Length, Regexp
from wtforms.fields import *
from flask_bootstrap import Bootstrap5, SwitchField
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from forms import login_form,register_form

from flask_bcrypt import Bcrypt
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InterfaceError,
    InvalidRequestError,
)
from werkzeug.routing import BuildError
from flask_bcrypt import Bcrypt,generate_password_hash, check_password_hash
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)


app = Flask(__name__)
app.secret_key = 'dev_secret'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"

# set default button sytle and size, will be overwritten by macro parameters
app.config['BOOTSTRAP_BTN_STYLE'] = 'primary'
app.config['BOOTSTRAP_BTN_SIZE'] = 'sm'

# set default icon title of table actions
app.config['BOOTSTRAP_TABLE_VIEW_TITLE'] = 'Read'
app.config['BOOTSTRAP_TABLE_EDIT_TITLE'] = 'Update'
app.config['BOOTSTRAP_TABLE_DELETE_TITLE'] = 'Remove'
app.config['BOOTSTRAP_TABLE_NEW_TITLE'] = 'Create'

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"

login_manager.init_app(app)

bootstrap = Bootstrap5(app)
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
bcrypt = Bcrypt()

class BootswatchForm(FlaskForm):
    """Form to test Bootswatch."""
    #DO NOT EDIT! Use list-bootswatch.py to generate the Radiofield below.
    theme_name = RadioField(
        default='default',
        choices=[
            ('default', 'none'),
            ('cerulean', 'Cerulean 5.3.1'),
            ('cosmo', 'Cosmo 5.3.1'),
            ('cyborg', 'Cyborg 5.3.1'),
            ('darkly', 'Darkly 5.3.1'),
            ('flatly', 'Flatly 5.3.1'),
            ('journal', 'Journal 5.3.1'),
            ('litera', 'Litera 5.3.1'),
            ('lumen', 'Lumen 5.3.1'),
            ('lux', 'Lux 5.3.1'),
            ('materia', 'Materia 5.3.1'),
            ('minty', 'Minty 5.3.1'),
            ('morph', 'Morph 5.3.1'),
            ('pulse', 'Pulse 5.3.1'),
            ('quartz', 'Quartz 5.3.1'),
            ('sandstone', 'Sandstone 5.3.1'),
            ('simplex', 'Simplex 5.3.1'),
            ('sketchy', 'Sketchy 5.3.1'),
            ('slate', 'Slate 5.3.1'),
            ('solar', 'Solar 5.3.1'),
            ('spacelab', 'Spacelab 5.3.1'),
            ('superhero', 'Superhero 5.3.1'),
            ('united', 'United 5.3.1'),
            ('vapor', 'Vapor 5.3.1'),
            ('yeti', 'Yeti 5.3.1'),
            ('zephyr', 'Zephyr 5.3.1'),
        ]
    )
    submit = SubmitField()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pwd = db.Column(db.String(300), nullable=False, unique=True)

    def __repr__(self):
        return '<User %r>' % self.username

@app.before_request
def session_handler():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    form = login_form()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user is None:
                flash("Invalid Username or password!", "danger")
            elif check_password_hash(user.pwd, form.pwd.data):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash("Invalid Username or password!", "danger")
        except Exception as e:
            flash(e, "danger")

    return render_template("auth.html",
        form=form,
        text="Login",
        title="Login",
        btn_action="Login"
        )

@app.route("/register/", methods=("GET", "POST"), strict_slashes=False)
def register():
    form = register_form()
    if form.validate_on_submit():
        try:
            email = form.email.data
            pwd = form.pwd.data
            username = form.username.data
            
            newuser = User(
                username=username,
                email=email,
                pwd=bcrypt.generate_password_hash(pwd),
            )
    
            db.session.add(newuser)
            db.session.commit()
            flash(f"Account Succesfully created", "success")
            return redirect(url_for("login"))

        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"User already exists!.", "warning")
        except DataError:
            db.session.rollback()
            flash(f"Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash(f"An error occured !", "danger")
    return render_template("auth.html",
        form=form,
        text="Create account",
        title="Register",
        btn_action="Register account"
        )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/collections")
@login_required
def collections():
    
    return render_template('collections.html')

@app.route('/form', methods=['GET', 'POST'])
def test_form():
    form = HelloForm()
    if form.validate_on_submit():
        flash('Form validated!')
        return redirect(url_for('index'))
    return render_template(
        'form.html',
        form=form,
        telephone_form=TelephoneForm(),
        contact_form=ContactForm(),
        im_form=IMForm(),
        button_form=ButtonForm(),
        example_form=ExampleForm()
    )


@app.route('/nav', methods=['GET', 'POST'])
def test_nav():
    return render_template('nav.html')


@app.route('/bootswatch', methods=['GET', 'POST'])
def test_bootswatch():
    form = BootswatchForm()
    if form.validate_on_submit():
        if form.theme_name.data == 'default':
            app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = None
        else:
            app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = form.theme_name.data
        flash(f'Render style has been set to {form.theme_name.data}.')
    else:
        if app.config['BOOTSTRAP_BOOTSWATCH_THEME'] != None:
            form.theme_name.data = app.config['BOOTSTRAP_BOOTSWATCH_THEME']
    return render_template('bootswatch.html', form=form)


@app.route('/pagination', methods=['GET', 'POST'])
def test_pagination():
    page = request.args.get('page', 1, type=int)
    pagination = Message.query.paginate(page=page, per_page=10)
    messages = pagination.items
    return render_template('pagination.html', pagination=pagination, messages=messages)


@app.route('/flash', methods=['GET', 'POST'])
def test_flash():
    flash('A simple default alert—check it out!')
    flash('A simple primary alert—check it out!', 'primary')
    flash('A simple secondary alert—check it out!', 'secondary')
    flash('A simple success alert—check it out!', 'success')
    flash('A simple danger alert—check it out!', 'danger')
    flash('A simple warning alert—check it out!', 'warning')
    flash('A simple info alert—check it out!', 'info')
    flash('A simple light alert—check it out!', 'light')
    flash('A simple dark alert—check it out!', 'dark')
    flash(Markup('A simple success alert with <a href="#" class="alert-link">an example link</a>. Give it a click if you like.'), 'success')
    return render_template('flash.html')


@app.route('/table')
def test_table():
    page = request.args.get('page', 1, type=int)
    pagination = Message.query.paginate(page=page, per_page=10)
    messages = pagination.items
    titles = [('id', '#'), ('text', 'Message'), ('author', 'Author'), ('category', 'Category'), ('draft', 'Draft'), ('create_time', 'Create Time')]
    data = []
    for msg in messages:
        data.append({'id': msg.id, 'text': msg.text, 'author': msg.author, 'category': msg.category, 'draft': msg.draft, 'create_time': msg.create_time})
    return render_template('table.html', messages=messages, titles=titles, Message=Message, data=data)


@app.route('/table/<int:message_id>/view')
def view_message(message_id):
    message = Message.query.get(message_id)
    if message:
        return f'Viewing {message_id} with text "{message.text}". Return to <a href="/table">table</a>.'
    return f'Could not view message {message_id} as it does not exist. Return to <a href="/table">table</a>.'


@app.route('/table/<int:message_id>/edit')
def edit_message(message_id):
    message = Message.query.get(message_id)
    if message:
        message.draft = not message.draft
        db.session.commit()
        return f'Message {message_id} has been editted by toggling draft status. Return to <a href="/table">table</a>.'
    return f'Message {message_id} did not exist and could therefore not be edited. Return to <a href="/table">table</a>.'


@app.route('/table/<int:message_id>/delete', methods=['POST'])
def delete_message(message_id):
    message = Message.query.get(message_id)
    if message:
        db.session.delete(message)
        db.session.commit()
        return f'Message {message_id} has been deleted. Return to <a href="/table">table</a>.'
    return f'Message {message_id} did not exist and could therefore not be deleted. Return to <a href="/table">table</a>.'


@app.route('/table/<int:message_id>/like')
def like_message(message_id):
    return f'Liked the message {message_id}. Return to <a href="/table">table</a>.'


@app.route('/table/new-message')
def new_message():
    return 'Here is the new message page. Return to <a href="/table">table</a>.'


@app.route('/icon')
def test_icon():
    return render_template('icon.html')


@app.route('/icons')
def test_icons():
    return render_template('icons.html')


if __name__ == '__main__':
    app.run(debug=True)
