import unittest
import sys
sys.path.append('/workspace/github-trending-scraper')
from app import create_app
from datetime import datetime

class AppTestCase(unittest.TestCase):

    def setUp(self):
        # Create a test client using the app factory
        self.app = create_app().test_client()
        self.app_context = create_app().app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'GitHub Trending', response.data)

    def test_trending_history_route(self):
        # Test with no date parameter
        response = self.app.get('/trending/history')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'GitHub Trending History', response.data)

        # Test with invalid date format
        response = self.app.get('/trending/history', query_string={'date': 'invalid-date'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid date format', response.data)

if __name__ == '__main__':
    unittest.main()