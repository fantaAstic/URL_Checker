# the file contains unittests for the url form submission and API call

import unittest, sys
from mock import MockForm, MockUser
from main import process_url_form_submission, check_safety_status
from models import URLs

sys.path.append('../webdev') # imports python file from parent directory
from app import app #imports flask app object

class FurtherTests(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site_testing.db'
        self.app = app.test_client()

    # unittest for the url_form function process_url_form_submission
    def test_successful_submission(self):
        # Prepare test data
        test_url = "https://example.com"
        test_form = MockForm(url=test_url)
        test_user = MockUser(is_authenticated=True, username="test_user")
        
        # Call the function
        result = process_url_form_submission(test_form, current_user=test_user)
        
        # Verify database changes
        url_obj = URLs.query.filter_by(url=test_url).first()
        self.assertIsNotNone(url_obj)
        self.assertEqual(url_obj.searched_by, "test_user")
        self.assertEqual(url_obj.total_searches, 1)
        
        # Verify flash message
        expected_flash_message = f'URL added to database: {test_url} (Safety status: ...)'
        self.assertIn(expected_flash_message, captured_flash_messages)
        
        # Verify function result
        self.assertEqual(result, (test_url, 200))

    # unittests for the safety status function check_safety_status   

    # test for a safe url
    def test_safe_url(self):
        url = "https://example.com"
        result = check_safety_status(url)
        self.assertEqual(result, "Safe")

    # test for an unsafe url
    def test_unsafe_url(self):
        url = "https://malicious.com"
        result = check_safety_status(url)
        self.assertIn("Unsafe", result)  # Check for presence of "Unsafe"

    # test for a failed request
    def test_failed_request(self):
        url = "https://example.com"  # Use a valid URL here
        result = check_safety_status(url)
        self.assertEqual(result, "Failed")

if __name__ == "__main__":
    unittest.main()
