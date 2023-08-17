# this file has the main helper function relating to the web routes in app.py

# necessary flask modules
from flask import flash, redirect, url_for, request
# the database tables in models.py
from models import User, URLs, db
# flask login modules to use in functions for login form submission
from flask_login import login_user, current_user
# datetime to display the time
from datetime import datetime
# requests module for API call
import requests

def handle_registration(form):
    try:
        if form.validate_on_submit(): # checks if form is submitted and passes validation checks
            existing_user = User.query.filter_by(username=form.username.data).first() # retrieves username already in database
            existing_email = User.query.filter_by(email=form.email.data).first() # retrieves email already in database
            
            if existing_user: # checks if username already exists
                flash('Username is already taken. Please choose a different username.', 'danger')
                return False
                
            if existing_email: # checks if email already exists
                flash('Email address is already registered. Please use a different email.', 'danger')
                return False
                
            if form.password.data != form.confirm_password.data: # checks if eneterd passwords match
                flash('Passwords do not match. Please make sure the passwords match.', 'danger')
                return False

            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)  # Hash the password before saving
            db.session.add(user) # add the user to the session
            db.session.commit() # add the user to the database
            
            flash(f'Account created for {form.username.data}!', 'success')
            
            users_with_consent = []

            if form.consent.data:
                users_with_consent.append(user) # alist storing users who have given consent for emails etc.
            
            return True  # Return True on successful registration
            
    except Exception as e:
        flash('An error occurred while creating the account. Please try again later.', 'danger')
        db.session.rollback()  # Rollback the changes to the database in case of an error
    
    return False  # Return False if registration failed

# Call to Google Safe Browsing API
def check_safety_status(url):
    api_key = 'AIzaSyBzRNE9NegrNTaZlgTjHVDYzranvqeIBBY'
    
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

    # Send the API request using a post request
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
            print(data) # for debugging purposes
            return "Safe"
        else:
            print(data)
            return "Unsafe - Threat Type: " + data['matches'][0]['threatType']  # Access threatType from data, shown in response so that users know   
    else:
        return "Failed"

# function to process the url form submission
def process_url_form_submission(form): # pass the form to function
    try:
        url = form.url.data
        # Call the Google Safe Browsing API
        safety_status = check_safety_status(url)

        # Get the username of the current user if logged in, otherwise store "Guest"
        username = current_user.username if current_user.is_authenticated else "Guest"

        # Save the URL and its safety status to the database
        url_obj = URLs.query.filter_by(url=url).first()
        if url_obj:
            # Update the searched_by attribute by adding the current username to the existing string
            url_obj.searched_by = url_obj.searched_by + ',' + username
            url_obj.total_searches += 1
        else: # create the url object to store in URLs table
            url_obj = URLs( 
                url=url,
                safety_status=safety_status,  # Assuming safety_status is a string, not a tuple
                search_date=datetime.now().date(),
                search_time=datetime.now().time(),
                searched_by=username
            )
            db.session.add(url_obj) # add the url obejct to the database table URLs

        db.session.commit() # commit the changes

        flash(f'URL added to database: {url} (Safety status: {safety_status})', 'success')
        return url, 200  # Success status code (200)

    except Exception as e:
        # Handle any other unexpected exceptions that may occur during the function execution
        return "Failed", 500  # Internal server error status code (500)

# function to process user login
def process_login_form_submission(form): # pass the form
    try:
        user = User.query.filter_by(username=form.username.data).first() # retrieves user from the user table in the database
        if user and user.check_password(form.password.data): # checks if user exists in the database
            login_user(user)
            next_page = request.args.get('next') # next parameter to store the URL the user attempted to access before being redirected to the login page
            return redirect(next_page) if next_page else redirect(url_for('url_form'))
        else:
            flash('Login Unsuccessful. Please check your username and password', 'danger') # if the user is not found in the database
            return False
    except Exception as e:
        print(f"An error occurred during login: {str(e)}")
        flash('Login Unsuccessful. An error occurred while processing your request.', 'danger')
        return False






