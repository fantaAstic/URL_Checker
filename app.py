# to contain only the running of the flask app and routes

from flask import Flask, render_template, url_for, flash, redirect, request, redirect, url_for, flash
from forms import RegistrationForm, URLForm, LoginForm
from flask_login import LoginManager, current_user, login_required, logout_user
from flask_behind_proxy import FlaskBehindProxy
import json
from flask_mail import Message, Mail
from main import handle_registration, process_url_form_submission, check_safety_status, process_login_form_submission
from models import db, User, URLs  # Import the db object and the models
import random
from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

app = Flask(__name__)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') # to protect secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site_dummy.db'

# Initialize the database with the Flask app
db.init_app(app)  # the db created in models - to avoid circular imports!

# db = SQLAlchemy(app) #for the unittest to work, otherwise I have two db objects, I have imported db from the models file

# Create all the tables
with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/test")
def test():
    return render_template('test.html')


users_with_consent = []


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    # send a welcome email to the user upon registration
    send_email()
    if handle_registration(form):
        # Redirect to the login page after successful registration
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


unsafe_urls = []


@app.route("/url_form", methods=['GET', 'POST'])
@login_required
def url_form():
    form = URLForm()
    if form.validate_on_submit():
        url, _ = process_url_form_submission(
            form)  # Extract the URL from the tuple
        # Redirect to the JSON response page
        return redirect(url_for('json_response', url=url))
    return render_template('url_form.html', title='Check URLs', form=form)


@app.route("/json_response/<path:url>", methods=['GET', 'POST'])
def json_response(url):
    # api_key = "9f6b5d4b45d6e73c37bdea9b3aa54610064052fe"  # check how many calls are left
    response_data = check_safety_status(url)

    if response_data:
        urls_data = URLs.query.all()
        return render_template(
            "json_response.html",
            json_response=json.dumps(response_data, indent=2),
            urls_data=urls_data,
            entered_url=url
        )
    else:
        flash(
            "Error occurred. Please check your API key or URL and try again.", "danger"
        )
        return redirect(url_for("home"))


login_manager = LoginManager(app)
login_manager.login_view = 'login'


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('url_form'))

    form = LoginForm()
    if form.validate_on_submit():
        if process_login_form_submission(form):
            return redirect(url_for('url_form'))

    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'CLASSIFIED'
app.config['MAIL_PASSWORD'] = 'CLASSIFIED'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# function to send emails


def send_email():
    form = RegistrationForm()
    if form.consent.data:  # Check if the consent box was checked
        # Send a welcome email to the user
        msg = Message("Welcome to Our Website!",
                      sender='fanta.kebe305@gmail.com', recipients=[form.email.data])
        msg.html = f"Thank you {form.username.data} for signing up on our website! We're excited to have you as a part of the community."
        mail.send(msg)

        # Add the user to the users_with_consent list
        # Or any identifier for the user
        users_with_consent.append(form.username.data)


# Assuming you have a list to store used random numbers
used_random_numbers = []


def generate_random_name(): # comment and why
    while True:
        random_number = random.randint(1, 9999)  # Adjust the range as needed
        if random_number not in used_random_numbers:
            used_random_numbers.append(random_number)
            return f"user_{random_number}"

# so that display usernmae function works


@app.context_processor
def inject_functions():
    return dict(display_username=display_username)


def display_username(form):
    form = RegistrationForm()
    if not form.consent.data:  # Check if the consent box was not checked
        random_name = generate_random_name()
        return random_name
    return form.username.data  # Return actual username if consent was given

# for pythonanywhere deployment
from flask import Flask, render_template, url_for, flash, redirect, request 
import git

@app.route("/update_server", methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('/home/URLCheckerF/URL_Checker') 
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
