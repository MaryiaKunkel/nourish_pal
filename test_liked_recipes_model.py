"""Liked recipes model tests."""

# run these tests like:
#
#    python3 -m unittest test_liked_recipes_model.py


import os
from unittest import TestCase

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

class LikedRecipesModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        History_recipes.query.delete()
        Liked_recipes.query.delete()

        self.client = app.test_client()

    def test_liked_recipes_model(self):
        
        user = User.signup(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='hashed_pwd'
        )
        db.session.commit()

        recipe_id = 1
        liked_recipe = Liked_recipes(user_id=user.id, recipe_id=recipe_id)
        db.session.add(liked_recipe)
        db.session.commit()

        self.assertEqual(liked_recipe.user_id, user.id)
        self.assertEqual(liked_recipe.recipe_id, recipe_id)