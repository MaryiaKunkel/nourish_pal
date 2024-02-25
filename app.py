import os, pdb, requests, re

from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from bs4 import BeautifulSoup
from mysecrets import API_SECRET_KEY
# from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from datetime import datetime

from forms import UserAddForm, LoginForm, EditProfileForm
from models import db, connect_db, User, History_recipes, Liked_recipes

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///nourishpal_db'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
# toolbar = DebugToolbarExtension(app)

connect_db(app)

with app.app_context():
    db.create_all()

app.app_context().push()
##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""
    # pdb.set_trace()
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                password=form.password.data
            )
            flash("Registration successful! Welcome to NourishPal.", 'success')
            db.session.commit()


        except IntegrityError:
            flash(f"User with email {form.email.data} already signed up", 'danger')
            return render_template('users/signup.html', form=form)
                    
        do_login(user)

        return redirect('/')

    else:
        return render_template('users/signup.html', form=form)
    




@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.email.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.first_name} {user.last_name}!", "success")
            session['email']=user.email
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)



@app.route('/logout')
def logout():
    """Handle logout of user."""

    # IMPLEMENT THIS
    if 'email' in session:
        session.clear()
        flash('You successfully logged out!', 'success')
    return redirect('/login')





@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = User.query.get_or_404(user_id)
    first_name=user.first_name
    last_name=user.last_name
    email=user.email

    return render_template('users/show.html', user=user, first_name=first_name, last_name=last_name, email=email)




@app.route('/users/<int:user_id>/edit', methods=["GET", "POST"])
def edit_profile(user_id):
    """Update profile for current user."""

    # IMPLEMENT THIS
    if 'email' not in session:
        flash ('Please login!', 'danger')
        return redirect('/login')  
    else:
        user=User.query.get_or_404(user_id)
        form=EditProfileForm(obj=user)
        if form.validate_on_submit():
            user.first_name=form.first_name.data
            user.last_name=form.last_name.data
            user.email=form.email.data
            password=form.password.data

            user=User.authenticate(user.email, password)

            if user:
                db.session.commit()
                return redirect(f'/users/{user_id}')
            else:
                flash("The password is incorrect!", 'danger')
                return redirect('/')
        return render_template('users/edit.html', form=form, user=user)
    

    
@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


@app.route('/users/<int:user_id>/favorites', methods=["GET", "POST"])
def users_favorites(user_id):
    """Show list of liked recipes of this user."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    fav_recipes=Liked_recipes.query.filter(user_id==user.id).all()
    liked_recipe_ids=[fav.recipe_id for fav in fav_recipes]

    ids_string=','.join(map(str, liked_recipe_ids))

    resp = requests.get(f"https://api.spoonacular.com/recipes/informationBulk", params={"apiKey": API_SECRET_KEY, "ids": ids_string})
    recipes = resp.json()

    for recipe in recipes:
        recipe['is_liked'] = recipe['id'] in liked_recipe_ids
    
    return render_template('users/favorites.html', user=user, recipes=recipes, liked_recipe_ids=liked_recipe_ids)


@app.route("/users/add_like/<int:recipe_id>", methods=['POST'])
def add_like(recipe_id):
    print('Route triggered with recipe_id:', recipe_id)
    user=User.query.get_or_404(g.user.id)
    existing_like=Liked_recipes.query.filter_by(user_id=user.id, recipe_id=recipe_id).first()

    if not existing_like:
        new_like=Liked_recipes(user_id=user.id, recipe_id=recipe_id)
        db.session.add(new_like)
    else: 
        db.session.delete(existing_like)
        
    db.session.commit()
    return jsonify({'is_liked': not existing_like})


@app.route('/users/<int:user_id>/history')
def view_history(user_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = User.query.get_or_404(user_id)

    # Get history recipes
    history_recipes = History_recipes.query.filter_by(user_id=g.user.id).order_by(desc(History_recipes.timestamp)).all()
    history_recipe_ids=[history_recipe.recipe_id for history_recipe in history_recipes]
    ids_string_history=','.join(map(str, history_recipe_ids))
    resp_history = requests.get(f"https://api.spoonacular.com/recipes/informationBulk", params={"apiKey": API_SECRET_KEY, "ids": ids_string_history})
    history_recipes = resp_history.json()

    # Get liked recipes
    fav_recipes=Liked_recipes.query.filter(user_id==user.id).all()
    liked_recipe_ids=[fav.recipe_id for fav in fav_recipes]


    for recipe in history_recipes:
        recipe['is_liked'] = recipe['id'] in liked_recipe_ids
    
    return render_template('users/history.html', user=user, recipes=history_recipes)





@app.route('/users/<int:user_id>/clear_history')
def clear_history(user_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    History_recipes.query.filter_by(user_id=g.user.id).delete()
    db.session.commit()
    flash('Recipe history cleared successfully.', 'success')
    return redirect(f'/users/{user_id}/history')







@app.route('/')
def home():
    """Show homepage"""

    if g.user:
        email=g.user.email
        user=User.query.filter_by(email=email).first()

    query = request.args.get('query')

    resp=requests.get("https://api.spoonacular.com/recipes/random?number=50", params={"apiKey": API_SECRET_KEY, 'query':query})
    data=resp.json()
    recipes=data.get('recipes')

    return render_template('home.html', recipes=recipes)



@app.route('/recipe/<int:recipe_id>')
def recipe_page(recipe_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    resp=requests.get("https://api.spoonacular.com/recipes/informationBulk", params={"apiKey": API_SECRET_KEY, 'ids': recipe_id})
    data=resp.json()
    recipe=data[0]
    title=data[0].get('title')
    image=data[0].get('image')
    instructions=data[0].get('analyzedInstructions')[0]['steps']
    summary_text=data[0].get('summary')
    tips_text=data[0].get('tips')['health']
    ingredients=data[0].get("extendedIngredients")

    user = g.user
    fav_recipes=Liked_recipes.query.filter(user.id==user.id).all()
    liked_recipe_ids=[fav.recipe_id for fav in fav_recipes]

    history_entry = History_recipes.query.filter_by(user_id=g.user.id, recipe_id=recipe_id).first()

    if history_entry:
        # If it exists, update the timestamp
        history_entry.timestamp = datetime.utcnow()
    else:
        # If it doesn't exist, add a new entry
        history_entry = History_recipes(user_id=user.id, recipe_id=recipe_id)
        db.session.add(history_entry)
    db.session.commit()

    resp2=requests.get("https://api.spoonacular.com/recipes/complexSearch", params={"apiKey": API_SECRET_KEY, 'veryPopular': 'true'})
    data2=resp2.json()
    recipes2=data2.get('results')


    return render_template('recipe.html', title=title, instructions=instructions, image=image, recipe=recipe, summary_text=summary_text, tips_text=tips_text, liked_recipe_ids=liked_recipe_ids, ingredients=ingredients, recipes2=recipes2)



@app.route('/search')
def search():
    if g.user:
        email=g.user.email
        user=User.query.filter_by(email=email).first()

        query = request.args.get('q')

        cuisine = request.args.getlist('cuisine')
        diet = request.args.getlist('diet')
        intolerance = request.args.getlist('intolerance')
        meal_type = request.args.getlist('type')
        include_ingredients = request.args.get('include-ingredients')
        exclude_ingredients = request.args.get('exclude-ingredients')
        max_time = request.args.get('maxTime')


        resp=requests.get("https://api.spoonacular.com/recipes/complexSearch", params={
            "apiKey": API_SECRET_KEY, 
            'query': query,
            'cuisine': ','.join(cuisine),
            'diet': ','.join(diet),
            'intolerance': ','.join(intolerance),
            'type': ','.join(meal_type),
            'includeIngredients': include_ingredients,
            'excludeIngredients': exclude_ingredients,
            'maxTime': max_time,
            'number':50
            })


        if resp.status_code == 200:
            # API request successful, parse the JSON response
            matching_recipes = resp.json()['results']
            # print(matching_recipes)
        else:
            # API request failed, handle the error (e.g., show an error message)
            matching_recipes = []
            # print(resp.content)
            # print(resp.status_code)



        return render_template('search_results.html', 
                               query=query, matching_recipes=matching_recipes,
                                cuisine=cuisine,
                                diet=diet,
                                intolerance=intolerance,
                                meal_type=meal_type,
                                include_ingredients=include_ingredients,
                                exclude_ingredients=exclude_ingredients,
                                max_time=max_time)
    


    return render_template('search.html')


@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req