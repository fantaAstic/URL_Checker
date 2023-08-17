# This file has all of the database tables

# use of sqlalchemy for database management
from flask_sqlalchemy import SQLAlchemy
# need the date and time for one of the columns
from datetime import datetime
# using werkzeug to hash passwords for user security
from werkzeug.security import generate_password_hash, check_password_hash
# provides default implementations for the methods required by Flask-Login to manage user sessions, easier to manage authentication etc.
from flask_login import UserMixin

db = SQLAlchemy() # initialises SQLAlchemy object for database tables

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
        self.search_date = datetime.now().date()  # Update search_date
        self.search_time = datetime.now().time()  # Update search_time
        db.session.commit()
    
    def get_searched_by_list(self): # to get a list of users who have searched the same url to avoid duplicates in the display of data
        # to show usernames
        # Split the searched_by string into a list of usernames
        usernames = self.searched_by.split(',')
        
        # Create a dictionary to store the username and their search count
        searched_by_dict = {}
        
        # Count the number of occurrences of each username in the list
        for username in usernames:
            searched_by_dict[username] = searched_by_dict.get(username, 0) + 1

        return searched_by_dict
