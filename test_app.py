"""App tests."""

# run these tests like:
#
#    FLASK_ENV=production python3 -m unittest test_app.py



import os
from unittest import TestCase


from models import db, User, History_recipes, Liked_recipes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///nourishpal_db"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        History_recipes.query.delete()
        Liked_recipes.query.delete()

        self.testuser = User.signup(first_name='Test',
                                    last_name='User',
                                    email="test@test.com",
                                    password="testuser"
                                    )
        
        db.session.commit()
        self.client = app.test_client()


    def tearDown(self):
        db.session.rollback()
        db.session.remove()


    def test_signup(self):
        """Test user signup."""

        with self.client as client:
            response = client.post('/signup', data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@test.com',
                'password': 'newpassword'
            }, follow_redirects=True)

            html = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Registration successful! Welcome to NourishPal.", html)


    def test_signup_existing_user(self):
        """Test user signup with an existing email."""

        with self.client as client:
            response = client.post('/signup', data={
                'first_name': 'Existing',
                'last_name': 'User',
                'email': 'test@test.com',
                'password': 'existingpassword'
            }, follow_redirects=True)

            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn("User with email test@test.com already signed up", html) 

   
    def test_signup_form_validation(self):
        """Test user signup form validation."""

        with self.client as client:
            # Test with missing required fields
            response = client.post('/signup', data={}, follow_redirects=True)

            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('This field is required.', html)

           
    def test_logout(self):
        """Test user logout."""

        with self.client as client:
            response_login = client.post('/login', data={
                'email': 'test@test.com',
                'password': 'testuser'
            }, follow_redirects=True)

            html_login = response_login.get_data(as_text=True)

            self.assertIn('Hello, Test User!', html_login)
            
            response_logout = client.get('/logout', follow_redirects=True)

            html_logout = response_logout.get_data(as_text=True)

            self.assertEqual(response_logout.status_code, 200)
            self.assertIn('You successfully logged out!', html_logout)
       

    def test_login_successful(self):
        """Test user login with correct credentials."""

        with self.client as client:
            response = client.post('/login', data={
                'email': 'test@test.com',
                'password': 'testuser'
            }, follow_redirects=True)

            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('Hello, Test User!', html)



    def test_view_own_profile(self):
        """Test that a user can view their own profile."""

        with self.client as client:
            response=client.post('/login', data={
                'email': 'test1@test.com',
                'password': 'testuser1'
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Welcome back', response.data) 
            


    def test_display_user_details(self):
        """Test that the correct user details are displayed on the profile page."""

        with self.client as client:
            client.post('/login', data={
                'email': 'test@test.com',
                'password': 'testuser'            
                }, follow_redirects=True)
            
            user = User.query.filter_by(email='test@test.com').first()

            response = client.get(f'/users/{user.id}', follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Test User', response.data)
            self.assertNotIn(b'Test2 User2', response.data)


    def test_successful_profile_edit(self):
        """Test that a logged-in user can successfully edit their profile."""

        with self.client as client:
            client.post('/login', data={
                'email': 'test@test.com',
                'password': 'testuser'
            }, follow_redirects=True)

            user = User.query.filter_by(email='test@test.com').first()

            response = client.post(f'/users/{user.id}/edit', data={
                'first_name': 'UpdatedFirstName',
                'last_name': 'UpdatedLastName',
                'email': 'test1@test.com',
                'password': 'updatedpassword'
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'UpdatedFirstName', response.data)


    def test_unauthorized_access_to_edit_profile(self):
        """Test that unauthorized access to edit profile is restricted."""

        with self.client as client:
            response = client.get('/users/1/edit', follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Please login!', response.data)


    def test_flash_messages_for_profile_edits(self):
        """Test that the correct flash messages are displayed for profile edits."""

        with self.client as client:
            client.post('/login', data={
                'email': 'test@test.com',
                'password': 'testuser'
            }, follow_redirects=True)

            user = User.query.filter_by(email='test@test.com').first()

            response = client.post(f'/users/{user.id}/edit', data={
                'first_name': '',
                'last_name': 'UpdatedLastName',
                'email': 'test1@test.com',
                'password': 'updatedpassword'
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'This field is required.', response.data)


    def test_redirect_after_successful_edit(self):
        """Test that the user is redirected to their profile page after a successful edit."""

        with self.client as client:
            client.post('/login', data={
                'email': 'test1@test.com',
                'password': 'testuser1'
            }, follow_redirects=True)

            user = User.query.filter_by(email='test@test.com').first()

            response = client.post(f'/users/{user.id}/edit', data={
                'first_name': 'UpdatedFirstName',
                'last_name': 'UpdatedLastName',
                'email': 'test1@test.com',
                'password': 'updatedpassword'
            }, follow_redirects=False)

            self.assertEqual(response.status_code, 302)


    def test_delete_user_successfully(self):
        """Test that a logged-in user can successfully delete their account."""
        
        with self.client as client:
            client.post('/login', data={'email': 'test@test.com', 'password': 'testuser'}, follow_redirects=True)

            response = client.post('/users/delete', follow_redirects=True)

            self.assertEqual(response.status_code, 200) 
            self.assertIn(b'Sign up', response.data)


    def test_unauthorized_access_to_delete_user(self):
        """Test that unauthorized access to delete user is restricted."""
        
        with self.client as client:

            response = client.post('/users/delete', follow_redirects=True)

            self.assertIn(b'Access unauthorized.', response.data)


    def test_redirect_after_account_deletion(self):
        """Test that the user is redirected to the signup page after account deletion."""
        
        with self.client as client:
            client.post('/login', data={'email': 'test@example.com', 'password': 'password'}, follow_redirects=True)

            response = client.post('/users/delete', follow_redirects=True)

            self.assertIn(b'Sign up', response.data) 


    def test_view_liked_recipes(self):
        """Test that a logged-in user can view their liked recipes."""
        
        with self.client as client:
            client.post('/login', data={'email': 'test@test.com', 'password': 'testuser'}, follow_redirects=True)

            user = User.query.filter_by(email='test@test.com').first()

            response = client.get(f'/users/{user.id}/favorites', follow_redirects=True)

            self.assertEqual(response.status_code, 200) 
            self.assertIn(b'Favorites', response.data) 


    def test_unauthorized_access_to_liked_recipes(self):
        """Test that unauthorized access to view favorites is restricted."""
        
        with self.client as client:

            response = client.get(f'/users/1/favorites', follow_redirects=True)

            self.assertIn(b'Access unauthorized.', response.data) 


    def test_display_liked_recipes(self):
        """Test that the liked recipes are displayed correctly."""
        
        with self.client as client:
            client.post('/login', data={'email': 'test@test.com', 'password': 'testuser'}, follow_redirects=True)

            user = User.query.filter_by(email='test@test.com').first()

            response = client.get(f'/users/{user.id}/favorites', follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Your favorite recipes:', response.data)  


    def test_view_recipe_history(self):
        """Test that a logged-in user can view their recipe history."""
        
        with self.client as client:
            client.post('/login', data={'email': 'test@test.com', 'password': 'testuser'}, follow_redirects=True)

            user = User.query.filter_by(email='test@test.com').first()

            response = client.get(f'/users/{user.id}/history', follow_redirects=True)

            self.assertEqual(response.status_code, 200) 
            self.assertIn(b'Your history:', response.data) 


    def test_unauthorized_access_to_recipe_history(self):
        """Test that unauthorized access to view history is restricted."""
        
        with self.client as client:

            user = User.query.filter_by(email='test@test.com').first()

            response = client.get(f'/users/{user.id}/history', follow_redirects=True)

            self.assertIn(b'Access unauthorized.', response.data)


    def test_display_recipe_history(self):
        """Test that the recipe history is displayed correctly."""
        
        with self.client as client:
            client.post('/login', data={'email': 'test@test.com', 'password': 'testuser'}, follow_redirects=True)

            user = User.query.filter_by(email='test@test.com').first()

            response = client.get(f'/users/{user.id}/history', follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Your history', response.data)




    def test_clear_recipe_history(self):
        """Test that a logged-in user can successfully clear their recipe history."""
        
        with self.client as client:
            client.post('/login', data={'email': 'test@test.com', 'password': 'testuser'}, follow_redirects=True)

            user = User.query.filter_by(email='test@test.com').first()
            recipe_id=1

            history_recipe = History_recipes.query.filter_by(user_id=user.id, recipe_id=recipe_id).first()
            print('fjvbcjhbvhjdbvhsbsbv', history_recipe)

            response = client.post(f'/users/{user.id}/clear_history', follow_redirects=True)

            self.assertEqual(response.status_code, 200) 
            self.assertIn(b'Recipe history cleared successfully.', response.data)
            

    def test_unauthorized_access_to_clear_recipe_history(self):
        """Test that unauthorized access to clear history is restricted."""
        with self.client as client:

            response = client.post('/users/1/clear_history', follow_redirects=True)

            self.assertIn(b'Access unauthorized.', response.data)
            

    def test_home_page_accessibility_logged_in_user(self):
        """Test that the home page is accessible to a logged-in user."""

        with self.client as client:
            client.post('/login', data={'email': 'test@test.com', 'password': 'testuser'}, follow_redirects=True)

            response = client.get('/', follow_redirects=True)

            self.assertEqual(response.status_code, 200) 
            self.assertIn(b'Test User', response.data) 


    def test_home_page_accessibility_not_logged_in_user(self):
        """Test that the home page is accessible to a not logged-in user."""

        with self.client as client:
            response = client.get('/', follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Sign up', response.data)


    def test_recipes_display_on_home_page(self):
        """Test that recipes are displayed on the home page."""

        with self.client as client:
            response = client.get('/', follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'<li class="recipe-li-home-page">', response.data) 


    def test_view_recipe_page_logged_in_user(self):
        """Test that a logged-in user can view a recipe page."""

        with self.client as client:
            client.post('/login', data={'email': 'test@test.com', 'password': 'testuser'}, follow_redirects=True)

            recipe_id=1

            response = client.get(f'/recipe/{recipe_id}', follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'<h3>Ingredients</h3>', response.data)


    def test_view_recipe_page_unauthorized_access(self):
        """Test that unauthorized access to view a recipe page is restricted."""

        with self.client as client:
            recipe_id=1
            response = client.get(f'/recipe/{recipe_id}', follow_redirects=True)

            self.assertIn(b'Access unauthorized', response.data)


    def test_search_page_accessibility_logged_in_user(self):
        """Test that the search page is accessible to a logged-in user."""

        with self.client as client:
            client.post('/login', data={'email': 'test@test.com', 'password': 'testuser'}, follow_redirects=True)

            response = client.get('/search', follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Search results', response.data)


    def test_search_page_accessibility_not_logged_in_user(self):
        """Test that the search page is accessible to a not logged-in user."""

        with self.client as client:
            response = client.get('/search', follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Search recipes', response.data)
            

    def test_search_with_parameters(self):
        """Test various search scenarios with different parameters."""

        with self.client as client:
            client.post('/login', data={'email': 'test@test.com', 'password': 'testuser'}, follow_redirects=True)
            
            response = client.get('/search?cuisine=italian&diet=vegetarian&include-ingredients=&exclude-ingredients=&maxTime=120', follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Cuisine: italian', response.data)
            self.assertIn(b'Diet: vegetarian', response.data)