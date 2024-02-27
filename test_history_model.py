"""History model tests."""

# run these tests like:
#
#    python3 -m unittest test_history_model.py


import os
from unittest import TestCase
from datetime import datetime

from models import db, User, History_recipes, Liked_recipes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///nourishpal_db"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class HistoryModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        History_recipes.query.delete()
        Liked_recipes.query.delete()

        self.client = app.test_client()

    def test_history_recipes_model(self):

        user = User.signup(
            first_name='John',
            last_name='Doe',
            email="john@example.com",
            password="HASHED_PASSWORD"
        )

        db.session.commit()

        recipe_id = 1
        history_recipe = History_recipes(user_id=user.id, recipe_id=recipe_id)
        db.session.add(history_recipe)
        db.session.commit()

        self.assertEqual(history_recipe.user_id, user.id)
        self.assertEqual(history_recipe.recipe_id, recipe_id)
        self.assertIsInstance(history_recipe.timestamp, datetime)


        
