import json
from unittest import TestCase
from model import Country, Indicators, News, connect_to_db, db, fake_data
from server import app
import server

class FlaskTestsBasic(TestCase):
    """Flask tests."""

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()

        app.config['TESTING'] = True

    def test_index(self):
        """Test homepage page."""

        result = self.client.get("/")
        self.assertIn("Select 2 countries", result.data)

    def test_metric(self):
        """Test about these metrics page"""

        result = self.client.get("/metrics")
        self.assertIn("Center for Systemic Peace", result.data)
        self.assertIn("GDP per capita is gross domestic product divided by midyear population", result.data)
        self.assertIn("regulatory environment", result.data)


class FlaskTestsDatabase(TestCase):

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

        connect_to_db(app, "postgresql:///testdb")

        db.create_all()

        fake_data()

    def tearDown(self):

        db.session.close()
        db.drop_all()

    def test_profile_page(self):
        """Test the country profile page"""

        result = self.client.get("/profile?countryone=Mars&countrytwo=Shakespeare")
        self.assertIn("Shakespeare", result.data)
        self.assertIn("Mars", result.data)
        self.assertIn("Ease of doing business", result.data)
        self.assertIn("full autocracy", result.data)
        self.assertIn("About these metrics", result.data)
        self.assertIn("Polity Time Series", result.data)
        self.assertIn("Per Capita GDP Time Series", result.data)








if __name__ == '__main__':
    import unittest
    unittest.main()
