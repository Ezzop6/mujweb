from flask import Blueprint, render_template

pojistenci_app_pages = Blueprint('pojistenci_app_pages', __name__)

@pojistenci_app_pages.route('/')
def main_page():
    return render_template('pojistenci_app/index.html')

@pojistenci_app_pages.route('/login', methods=['GET', 'POST'])
def login_page():
    '''Login page'''
    return render_template('pojistenci_app/login.html')

