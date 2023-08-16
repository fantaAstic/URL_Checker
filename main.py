# to contain the functions, exception etc related to the web page

from flask import flash, redirect, url_for, request
from models import User, URLs, db
from flask_login import login_user, current_user
from datetime import datetime
import requests
import os


def handle_registration(form):
    try:
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)  # Hash the password before saving
            db.session.add(user)
            db.session.commit()
            flash(f'Account created for {form.username.data}!', 'success')
            if form.consent.data:
                users_with_consent.append(user)
            return redirect(url_for('login'), code=200)  # Correct way to set the status code
    except Exception as e:
        flash('An error occurred while creating the account. Please try again later.', 'danger')
        db.session.rollback()  # Rollback the changes to the database in case of an error
    return False

# core piece
def check_safety_status(url):
    api_key = os.environ.get('API_KEY')
    
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
            print(data)
            return "Safe"
        else:
            print(data)
            return "Unsafe - Threat Type: " + data['matches'][0]['threatType']  # Access threatType from data    
    else:
        return "Failed"


def process_url_form_submission(form): # pass url and current user instead of the form
    try:
        url = form.url.data
        # Call the Google Safe Browsing API
        safety_status = check_safety_status(url)

        # Get the username of the current user if logged in, else store "Guest"
        username = current_user.username if current_user.is_authenticated else "Guest"
        if current_user.is_authenticated:
            username = current_user.username
        else:
            return redirect(url_for('login', url=url)), 401  # Unauthorized status code (401)

        # Save the URL and its safety status to the database
        url_obj = URLs.query.filter_by(url=url).first()
        if url_obj:
            # Update the searched_by attribute by adding the current username to the existing string
            url_obj.searched_by = url_obj.searched_by + ',' + username
            url_obj.total_searches += 1
        else:
            url_obj = URLs(
                url=url,
                safety_status=safety_status,  # Assuming safety_status is a string, not a tuple
                search_date=datetime.now().date(),
                search_time=datetime.now().time(),
                searched_by=username
            )
            db.session.add(url_obj)

        db.session.commit()

        if safety_status == "Unsafe":  # a list of unsafe urls
            unsafe_urls.append(url)

        flash(f'URL added to database: {url} (Safety status: {safety_status})', 'success')
        return url, 200  # Success status code (200)

    except Exception as e:
        # Handle any other unexpected exceptions that may occur during the function execution
        return "Failed", 500  # Internal server error status code (500)


def process_login_form_submission(form): #just need user details
    try:
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('url_form'))
        else:
            flash('Login Unsuccessful. Please check your username and password', 'danger')
            return False
    except Exception as e:
        # Handle any unexpected exceptions that might occur during the login process
        # You can log the error for debugging purposes
        print(f"An error occurred during login: {str(e)}")
        flash('Login Unsuccessful. An error occurred while processing your request.', 'danger')
        return False

users_with_consent = []





