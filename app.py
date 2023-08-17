# This file contains the main flask web routes, emailing functions and a function for automating deployment

# necessary flask imports
from flask import Flask, render_template, url_for, flash, redirect, request, redirect, url_for, flash
# the forms that I created in forms.py to be used
from forms import RegistrationForm, URLForm, LoginForm
# flask_login module to handle user login and logout
from flask_login import LoginManager, current_user, login_required, logout_user
# useful for deployment and security
from flask_behind_proxy import FlaskBehindProxy
# to handle the json response from the API
import json
# to handle the emailing function
from flask_mail import Message, Mail
# the main helper functions that are used in each web route
from main import handle_registration, process_url_form_submission, check_safety_status, process_login_form_submission
# the tables created by SQLAlchemy and stored in the site_dummy database
from models import db, User, URLs  # Import the db object and the models
# for the generartion of random numbers to create a random username
import random
# for deployment
import git
# to protect secret keys
import os

app = Flask(__name__) # creates a Flask web application instance
proxied = FlaskBehindProxy(app) # to set up flaskbehindproxy
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') # to protect secret key # setting the secret key for session management, without this can't register, login
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site_dummy.db' # database connection

# Initialize the database with the Flask app
db.init_app(app)  # the db created in models - to avoid circular imports!

# Create all the tables from models.py
with app.app_context():
    db.create_all()

# email configuration using Google's SMTP server and flask extension
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'fanta.kebe305@gmail.com'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# route for the home page
@app.route("/")
def home():
    return render_template('home.html')

# route for the about page
@app.route("/about")
def about():
    return render_template('about.html')


users_with_consent = [] # a list to store users who give consent upon registration

# route for the register page
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    # send a welcome email to the user upon registration
    send_email()
    if handle_registration(form):
        # Redirect to the login page after successful registration
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# route for the url checking form
@app.route("/url_form", methods=['GET', 'POST'])
def url_form():
    form = URLForm()
    if form.validate_on_submit():
        url, _ = process_url_form_submission(
            form)  # Extract the URL from the tuple
        # Redirect to the JSON response page
        return redirect(url_for('json_response', url=url))
    return render_template('url_form.html', title='Check URLs', form=form)

# route for the response after a url is queried
@app.route("/json_response/<path:url>", methods=['GET', 'POST'])
def json_response(url):
    response_data = check_safety_status(url) # make a call to the Google Safe Browsing API to determine whether or not the url is safe

    if response_data:
        urls_data = URLs.query.all() # getting the data from the urls table
        return render_template(
            "json_response.html",
            json_response=json.dumps(response_data, indent=2), # formatting the json response
            urls_data=urls_data, # passing the data from the urls table to the html page
            entered_url=url # passing the entered url to the html page
        )
    else:
        flash(
            "Error occurred. Please check your API key or URL and try again.", "danger" # if there is an error 
        )
        return redirect(url_for("home"))

# to manage user login and logout
login_manager = LoginManager(app) # initializes the LoginManager instance using the Flask application instance app
login_manager.login_view = 'login' # sets the login_view (i.e. endpoiny) attribute of the LoginManager instance, should I have any pages that require login

# route for the login page
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: # checks if current user is authenticated
        return redirect(url_for('url_form'))

    form = LoginForm() # instance of the user login form
    if form.validate_on_submit(): # checks if the form has been submitted and passes the validation checks
        if process_login_form_submission(form):
            return redirect(url_for('url_form'))

    return render_template('login.html', title='Login', form=form)

# route for the logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home')) # when users logout they are taken to the home page

# retrieves a user object from the database based on the user's ID - to store in the session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# function to send welcome email
def send_email():
    form = RegistrationForm()

    if form.consent.data:  # Check if the consent box was checked
        try:
            if form.consent.data:  # Check if the consent box was checked
                # Query the most searched URL
                most_searched_url = URLs.query.order_by(URLs.total_searches.desc()).first()

                # Prepare the HTML content for the email
                html_content = f"Thank you {form.username.data} for signing up on our website! We're excited to have you as a part of the community.<br><br>"
                html_content += "<strong>Most Searched URL:</strong><br>"
                html_content += f"URL: {most_searched_url.url}, Searches: {most_searched_url.total_searches}"

                # Send the email
                msg = Message("Welcome to Our Website!",
                            sender='fanta.kebe305@gmail.com', recipients=[form.email.data])
                msg.html = html_content
                mail.send(msg)

                # Flash a success message
                flash("Email sent successfully", "success")

        except Exception as e:
            # Flash an error message
            flash(f"An error occurred: {str(e)}", "error")

# generates a random username to be displayed in the search history table
def generate_random_name(): 
    # A list to store used random numbers, so that no two users get the same random usernmane
    used_random_numbers = []
    while True: # a loop to keep generating random numbers and checking their uniqueness.
        random_number = random.randint(1, 9999)  # Adjust the range as needed, not sure about site traffic yet
        if random_number not in used_random_numbers: # if the number hasn't already been used
            used_random_numbers.append(random_number)
            return f"user_{random_number}" # returns user_random_number

# so that display username function works, adds the name variables to the json_response template context
@app.context_processor
def inject_functions():
    return dict(display_username=display_username)

# generates random name for all users
def display_username(form):
    form = RegistrationForm()
    if not form.consent.data:  # Check if the consent box was not checked
        random_name = generate_random_name()
        return random_name
    return form.username.data  # Return actual username if consent was given

# for python anywhere deployment
@app.route("/update_server", methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('/home/URLCheckerF/URL_Checker') 
        origin = repo.remotes.origin
        origin.pull() # pulls (fetches and merges) the latest changes from the remote repository into the local repository - updates pythonaywhere codebase
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
