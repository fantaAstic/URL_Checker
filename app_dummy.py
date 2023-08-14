from flask import Flask, render_template, url_for, flash, redirect, request
from forms import RegistrationForm, URLForm, LoginForm
from flask_login import UserMixin, LoginManager, login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_behind_proxy import FlaskBehindProxy
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import json

app = Flask(__name__)
proxied = FlaskBehindProxy(app)  ## add this line
app.config['SECRET_KEY'] = 'CLASSIFIED'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site_test.db' 

db = SQLAlchemy(app)

#creating the Users table
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def set_password(self, password):
            self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

#creating the URLs table

class URLs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    safety_status = db.Column(db.String(12), nullable=False)
    search_date = db.Column(db.Date, nullable=False, default=datetime.now().date())
    search_time = db.Column(db.Time, nullable=False, default=datetime.now().time())
    total_searches = db.Column(db.Integer, nullable=False, default=1)
    searched_by = db.Column(db.Text, nullable=False, default='Guest')

    def __repr__(self):
        return f"URL('{self.url}')"

    def increment_total_searches(self):
        self.total_searches += 1
        db.session.commit()
    
    def get_searched_by_list(self):
        # Split the searched_by string into a list of usernames
        usernames = self.searched_by.split(',')
        
        # Create a dictionary to store the username and their search count
        searched_by_dict = {}
        
        # Count the number of occurrences of each username in the list
        for username in usernames:
            searched_by_dict[username] = searched_by_dict.get(username, 0) + 1

        return searched_by_dict

# Create all the tables
with app.app_context():
    db.create_all() 

@app.route("/")                          # this tells you the URL the method below is related to
def home():
    return render_template('home.html')    

@app.route("/about")                          # this tells you the URL the method below is related to
def about():
    return render_template('about.html')  

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)  # Hash the password before saving
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))  # Redirect to the login page after successful registration
    return render_template('register.html', title='Register', form=form)

unsafe_urls = []

from datetime import datetime

@app.route("/url_form", methods=['GET', 'POST'])
def url_form():
    form = URLForm()
    if form.validate_on_submit():
        url = form.url.data
        # Call the Google Safe Browsing API
        safety_status = check_safety_status(url)

        # Get the username of the current user if logged in, else store "Guest"
        username = current_user.username if current_user.is_authenticated else "Guest"
        if current_user.is_authenticated:
            username = current_user.username
        else:
            return redirect(url_for('login', url=url))

        # Save the URL and its safety status to the database
        url_obj = URLs.query.filter_by(url=url).first()
        if url_obj:
            # Update the searched_by attribute by adding the current username to the existing string
            url_obj.searched_by = url_obj.searched_by + ',' + username
            url_obj.total_searches += 1
        else:
            url_obj = URLs(url=url, safety_status=safety_status, search_date=datetime.now().date(), search_time=datetime.now().time(), searched_by=username)
            db.session.add(url_obj)

        db.session.commit()

        if safety_status == "Unsafe":  # a list of unsafe urls
            unsafe_urls.append(url)
        flash(f'URL added to database: {url} (Safety status: {safety_status})', 'success')
        return redirect(url_for('json_response', url=url))  # Redirect to the JSON response page

    return render_template('url_form.html', title='Check URLs', form=form)


def check_safety_status(url):
    api_key = "CLASSIFIED"
    
    # Construct the request payload
    payload = {
        "client": {
            "clientId": "969300417709-p0it24usbl1qbbf09gpv1ed9fm765qaq.apps.googleusercontent.com",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }

# Send the request using a post request
    response = requests.post(
        "https://safebrowsing.googleapis.com/v4/threatMatches:find", 
        headers={"Content-Type": "application/json"},
        params={"key": api_key},
        json=payload
    )

    # Check the response and return the safety status based on the response
    if response.status_code == 200:
        data = response.json()
        if not data:  # If the URL returns an empty JSON response, no threat has been detected
            return "Safe"
        else:
            return "Unsafe"
    else:
        return "Failed"

def check_url_with_apivoid(api_key, url):
    endpoint = f"https://endpoint.apivoid.com/urlrep/v1/pay-as-you-go/?key={api_key}&url={url}"
    response = requests.get(endpoint)
    json_data = response.json()
    return json_data


@app.route("/json_response/<path:url>", methods=['GET', 'POST'])
def json_response(url):
    api_key = "CLASSIFIED" 
    response_data = check_url_with_apivoid(api_key, url)

    if response_data:
        urls_data = URLs.query.all()
        return render_template(
            "json_response.html",
            json_response=json.dumps(response_data, indent=2),
            urls_data=urls_data,
        )

    else:
        flash(
            "Error occurred. Please check your API key or URL and try again.", "danger"
        )
        return redirect(url_for("home"))
 
# urls_data = URLs.query.all()
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('url_form'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('url_form'))
        else:
            flash('Login Unsuccessful. Please check your username and password', 'danger')

    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__': 
    app.run(debug=True, host="0.0.0.0")
