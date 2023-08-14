import unittest, sys, os
from flask_sqlalchemy import SQLAlchemy

sys.path.append('../webdev') # imports python file from parent directory
from app import app, db

class UsersTests(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site_testing.db'
        self.app = app.test_client()

    ###############
    #### tests ####
    ###############

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

# need to add following logic in html response before actually being able to test it.
    '''
    def test_existing_user_registration(self):
        # Register the first user
        response = self.register('test', 'test@example.com', 'FlaskIsAwesome')
        self.assertEqual(response.status_code, 200)
        
        # Attempt to register a user with the same username or email
        response = self.register('test', 'test2@example.com', 'AnotherPassword')
        self.assertIn(b'Username already taken.', response.data)
        
        response = self.register('anotheruser', 'test@example.com', 'YetAnotherPassword')
        self.assertIn(b'Email already taken.', response.data)
    
    
    def test_password_mismatch_registration(self):
        response = self.register('test', 'test@example.com', 'Password123', 'MismatchedPassword')
        self.assertIn(b'Passwords must match.', response.data)

    def test_weak_password_registration(self):
        response = self.register('test', 'test@example.com', 'weak', 'weak')
        self.assertIn(b'Password must be at least 8 characters long and contain', response.data)

    def test_successful_login_after_registration(self):
        # Register a user
        self.register('test', 'test@example.com', 'FlaskIsAwesome')
        
        # Log in with the registered credentials
        response = self.app.post('/login', data=dict(
            username='test',
            password='FlaskIsAwesome'
        ), follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Logged in successfully.', response.data)
    
    def test_unsuccessful_login_after_registration(self):
        # Register a user
        self.register('test', 'test@example.com', 'FlaskIsAwesome')
        
        # Attempt to log in with incorrect password
        response = self.app.post('/login', data=dict(
            username='test',
            password='WrongPassword'
        ), follow_redirects=True)
        
        self.assertIn(b'Invalid username or password.', response.data)
'''
    # checks if a username is betweeen 2 - 20 characters, otherwise, their username is invalid
    def test_invalid_username_registration(self):
        response = self.register('t', 'test@example.com', 'FlaskIsAwesome')
        self.assertIn(b'Field must be between 2 and 20 characters long.', response.data)

    # checks if the email entered is an actual email domain, and has the .com or .co.uk or .org at the end
    def test_invalid_email_registration(self):
        response = self.register('test2', 'test@example', 'FlaskIsAwesome')
        self.assertIn(b'Invalid email address.', response.data)


if __name__ == "__main__":
    unittest.main()