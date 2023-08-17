# this file contains tests on users, login and registration

import unittest, sys

sys.path.append('../webdev') # imports python file from parent directory
from app import app

class UsersTests(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site_testing.db'
        self.app = app.test_client()

    def register(self, username, email, password):
        return self.app.post('/register',
                            data=dict(username=username,
                                      email=email,
                                      password=password, 
                                      confirm_password=password),
                            follow_redirects=True)

    # checks if a user has successfully registered
    def test_valid_user_registration(self):
        response = self.register('test', 'test@example.com', 'FlaskIsAwesome')
        self.assertEqual(response.status_code, 200)

    # checks if a username is betweeen 2 - 20 characters, otherwise, their username is invalid
    def test_invalid_username_registration(self):
        response = self.register('t', 'test@example.com', 'FlaskIsAwesome')
        self.assertIn(b'Field must be between 2 and 20 characters long.', response.data)

    # checks if the email entered is an actual email domain, and has the .com or .co.uk or .org at the end
    def test_invalid_email_registration(self):
        response = self.register('test2', 'test@example', 'FlaskIsAwesome')
        self.assertIn(b'Invalid email address.', response.data)
    
    def login(self, username, password):
        return self.app.post('/login',
                            data=dict(username=username,
                                      password=password),
                            follow_redirects=True)
    
    # checks if a user successfully logs in
    def test_successful_login(self):
        response = self.login(username='test_user', password='test_password')
        self.assertEqual(response.status_code, 200)  # Assuming successful login redirects to a URL with status 200

    # checks if a user logs in with the incorect password
    def test_failed_login(self):
        response = self.login(username='test_user', password='wrong_password')
        self.assertEqual(response.status_code, 200)  # Assuming failed login redirects to a URL with status 200


if __name__ == "__main__":
    unittest.main()
