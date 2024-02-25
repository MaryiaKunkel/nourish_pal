"""User model tests."""

# run these tests like:
#
#    python3 -m unittest test_user_model.py


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

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        History_recipes.query.delete()
        Liked_recipes.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            first_name='First_name',
            last_name='Last_name',
            email="test@test.com",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.history_recipes), 0)
        self.assertEqual(len(u.liked_recipes), 0)

    def test_user_repr(self):
        '''Does the repr method work as expected?'''
        u = User(
            first_name='First_name',
            last_name='Last_name',
            email="test@test.com",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(repr(u), f"<User #{u.id}: First_name Last_name, test@test.com>")


    def test_signup(self):
        '''Does User.create successfully create a new user given valid credentials'''
        user1 = User.signup(
            first_name='First_name1',
            last_name='Last_name1',
            email='email1@gmail.com',
            password='hashed_pwd'
        )
        db.session.commit()

        self.assertIsInstance(user1, User)
        self.assertIsNotNone(User.query.filter_by(email='email1@gmail.com').first())
        self.assertTrue(user1.password, 'hashed_pwd')

        user2 = User.signup(
            first_name='First_name2',
            last_name='Last_name2',
            email='email2@gmail.com',
            password='hashed_pwd2'
        )
        db.session.commit()
        
        self.assertIsInstance(user2, User)
        self.assertIsNotNone(User.query.filter_by(email='email2@gmail.com').first())
        self.assertTrue(user2.password, 'hashed_pwd2')

    def test_authenticate(self):
        '''Does User.authenticate successfully return a user when given a valid email and password?'''
        user1 = User.signup(
            first_name='First_name1',
            last_name='Last_name1',
            email="test@test.com",
            password="HASHED_PASSWORD",
        )

        db.session.commit()

        authenticated_user = User.authenticate(email="test@test.com", password='HASHED_PASSWORD')

        self.assertIsInstance(user1, User)
        self.assertEqual(authenticated_user.email, 'test@test.com')

        wrong_password_user=User.authenticate(email="test@test.com", password='wrong_password')

        self.assertFalse(wrong_password_user)