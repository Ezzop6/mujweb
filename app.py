import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
debug = os.environ.get("DEBUG") == "True"

user_for_debuging = os.environ.get("USER_FOR_DEBUGING")
from my_packages._tools import *
from my_packages.vtipky import error_page_joke
from bl_pages.main_pages import main_pages
from bl_pages.pojistenci_app_pages import pojistenci_app_pages
from bl_pages.smenost_app_pages import smenost_app_pages
from database import DbUsersMain


from flask_wtf.csrf import CSRFProtect, CSRFError
from flask import Flask, render_template, redirect, url_for, g, session
from flask_login import current_user, LoginManager, UserMixin, login_user, logout_user
import os

db = DbUsersMain()
login_manager = LoginManager()


app = Flask(__name__)
csrf = CSRFProtect(app)
app.config['PERMANENT_SESSION_LIFETIME'] = 7200 # time to logout user
app.config['WTF_CSRF_TIME_LIMIT'] = 3600
app.config['SECRET_KEY'] = random_secret_key()


login_manager.init_app(app)


app.register_blueprint(main_pages, url_prefix='/')
app.register_blueprint(pojistenci_app_pages, url_prefix='/pojistenci_app')
app.register_blueprint(smenost_app_pages, url_prefix='/KalendarSmen_app')

@app.before_request
def before_request():
    g.user = None
    if "user" in session:
        g.user = session["user"]
        
@login_manager.user_loader
def load_user(user_id):
    '''Callback to reload the user object from the user ID stored in the session'''
    return User(user_id)

        
'''error pages'''
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
def access_denied(error):
    error_code = str(error.code)
    message = error_page_joke(error_code)
    if error_code == '401':
        return render_template('401.html', error=error, message=message)
    elif error_code == '403':
        return render_template('403.html', error=error, message=message)
    elif error_code == '404':
        return render_template('404.html', error=error, message=message)

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return e.description

# for debuging
if debug:
    @app.route('/login_test_user')
    def login_test_user():
        '''Login test user'''
        current_user = User("6411f76b45aae9e67c066141")
        login_user(current_user)
        return redirect(url_for('main_pages.main_page'))
    
@app.route('/logout_test_user')
def logout_test_user():
    '''Logout test user'''
    logout_user()
    return redirect(url_for('main_pages.main_page'))




class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.role = db.get_user_role(self.id)
        self.login = db.get_user_login(self.id)
        



if __name__ == '__main__':
    if debug:
        app.debug = True
        cprint("Debug mode is ON")
    host = os.getenv('IP', '0.0.0.0')
    port = int(os.getenv('PORT', 3000))
    app.jinja_env.globals.update(get_random_produkt_img = get_random_produkt_img)
    app.jinja_env.globals.update(debug = debug)
    app.run(host=host, port=port)