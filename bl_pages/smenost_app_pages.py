from flask import Blueprint, render_template

smenost_app_pages = Blueprint('smenost_app_pages', __name__)

@smenost_app_pages.route('/')
def main_page():
    return render_template('smenost_app/index.html')

