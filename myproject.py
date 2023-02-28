"""Below are the modules required for the routes in this document."""
from dbFunctions import get_likes, delete_like, get_stories
from dbFunctions import check_admin, add_user, add_dislike, add_like
from dbFunctions import get_dislikes, delete_dislike
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for
from flask_talisman import Talisman

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
Talisman(app)
app.secret_key = env.get("APP_SECRET_KEY")

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

@app.route("/login")
def login():
    """This function will return the redirect to Auth0."""
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    """
    This function assigns the access token to the user once logged in.
    The user is then redirected to /logUser.
    """
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/logUser")

@app.route("/logUser", methods=['GET', 'POST'])
def logUser():
    """
    This function gets the userID, name, and admin privilege from the current session.
    They are passed into add_user from dbFunctions for insert into database.
    User is then redirected to home "/".
    """
    userID = str(session['user']['userinfo']['email'])
    name = str(session['user']['userinfo']['name'])
    admin = 0
    add_user(userID, name, admin)
    return redirect("/")

@app.route("/logout")
def logout():
    """
    This function describes what happens when the user logs out.
    The session is cleared and logout is handled by Auth0.
    """
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route("/")
def home():
    """
    This function describes the home or "/" route.
    The stories are pulled from db using get_stories then passed
    into the template home.html to display them.
    User is also passed in to display current user's name.
    """
    try:
        stories = get_stories()
        return render_template('home.html', stories=stories, session=session.get('user'))
    except Exception as e:
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text

@app.route("/<int:story_ID>/<string:story_title>/likes/", methods=['GET', 'POST'])
def likes(story_ID, story_title):
    """
    This function is a redirect from the like button in home.html and passes a like
    into the database using add_like from dbFunctions.
    The user is then redirected back to home.
    """
    user_ID = str(session['user']['userinfo']['email'])
    add_like(story_ID, user_ID, story_title)
    return redirect("/")

@app.route("/<int:story_ID>/<string:story_title>/dislikes/", methods=['GET', 'POST'])
def dislikes(story_ID, story_title):
    """
    This function is a redirect from the add_dislike button in home.html and passes a like
    into the database using add_dislike from dbFunctions.
    The user is then redirected back to home.
    """
    user_ID = str(session['user']['userinfo']['email'])
    add_dislike(story_ID, user_ID, story_title)
    return redirect("/")

@app.route("/<int:story_ID>/<string:user_ID>/deleteLike/", methods=['GET', 'POST'])
def deleteLike(story_ID, user_ID):
    """
    This function is redirect from selecting the delete button in admin.html.
    Passes the current user and story to delete in delete_like from dbFunctions.
    User is redirected back into /adminLike.
    """
    #user_ID = str(session['user']['userinfo']['email'])
    delete_like(story_ID, user_ID)
    return redirect("/adminLike")

@app.route("/<int:story_ID>/<string:user_ID>/deleteDislike/", methods=['GET', 'POST'])
def deleteDislike(story_ID, user_ID):
    """
    This function is redirect from selecting the delete button in admin.html.
    Passes the current user and story to delete in delete_dislike from 
    dbFunctions. User is redirected back into /adminDislike.
    """
    #user_ID = str(session['user']['userinfo']['email'])
    delete_dislike(story_ID, user_ID)
    return redirect("/adminDislike")

@app.route("/admin")
def admin():
    """
    This function either shows admin page or a page telling user they
    don't have admin access. The admin.html page is rendered with the 
    two buttons to manage either likes or dislikes.
    """
    user_ID = str(session['user']['userinfo']['email'])
    if check_admin(user_ID) == False:
        return render_template('notAdmin.html', session=session.get('user'))
    else:
        return render_template('admin.html', session=session.get('user'))

@app.route("/adminLike")
def adminLike():
    """
    This function gets the likes from the database using get_likes.
    The admin.html page is rendered with the current likes.
    """
    likes = get_likes()
    return render_template('likesAdmin.html', likes=likes, session=session.get('user'))

@app.route("/adminDislike")
def adminDislike():
    """
    This function gets the dislikes from the database using get_dislikes.
    The admin.html page is rendered with the current dislikes.
    """
    dislikes = get_dislikes()
    return render_template('dislikesAdmin.html', dislikes=dislikes, session=session.get('user'))

@app.route("/profile")
def profile():
    """
    This function renders profile.html, where the current user and email is displayed.
    """
    return render_template('profile.html', session=session.get('user'))

if __name__ == "__main__":
    app.run(host='0.0.0.0')
