import unittest, sys

from main import handle_registration, check_safety_status, check_url_with_apivoid, process_url_form_submission, process_login_form_submission

from app import home, about, register, url_form, json_response, login, logout, load_user

sys.path.append('../webdev') # imports python file from parent directory
from app import app, db #imports flask app object

class BasicTests(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site_testing.db'
        self.app = app.test_client()

    ###############
    #### tests ####
    ###############

    # unittests for the website pages, will have ok status code if the webpage works

    # unittest for the home page
    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    

    # unittest for the about page
    def test_about_page(self):
        response = self.app.get('/about', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    

    # unittest for the register page
    def test_register_page(self):
        response = self.app.get('/register', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    

    # unittest for the url form page
    def test_url_form_page(self):
        response = self.app.get('/url_form', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    

    # unittest for the login page
    def test_login_page(self):
        response = self.app.get('/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    

    # unittest for the logout page
    def test_logout_page(self):
        response = self.app.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    
    # unittest for the json response page
    def test_json_response_page(self):
        response = self.app.get('/json_response/<path:url>', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()