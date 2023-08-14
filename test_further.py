# are these tests really necessary, as aren't they already being tested within the routes?

import unittest, sys

from flask import Flask

from flask_sqlalchemy import SQLAlchemy

sys.path.append('../webdev') # imports python file from parent directory
from app import app, db #imports flask app object

class FurtherTests(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site_testing.db'
        self.app = app.test_client()

    
    # unittest for the login function process_login_form_submission


    # unittest for the url_form function process_url_form_submission


    # unittest for the safety status function check_safety_status


    # unittest for the check url API call function check_url_with_apivoid

if __name__ == "__main__":
    unittest.main()
